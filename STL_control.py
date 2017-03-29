"""
Here we synthesize controllers from STL
Sadra Sadraddini
"""

from gurobipy import *
import random

class STL_system:
    def __init__(self,n,m,p):
        self.model=Model("STL_Spec")
        self.x={}
        self.u={}
        self.y={}
        self.z={}
        self.T=0
        self.A={}
        self.B={}
        self.c={}
        self.Dw={}
        self.dw={}
        self.g={}
        self.formulas={} #key: name, val: dictionary of t variables
        self.n=n
        self.m=m
        self.p=p
        self.M=1000
        
        self.Ex_row=1
        self.Ex={}
        self.ex={} # Hx < h characterizes ||Ex||_\infty <=1

        self.Fu_row=1
        self.Fu={}
        self.fu={} # Hx < h characterizes ||Fu||_\infty <=1        
    
    def matrix_installation(self):
        n=self.n
        m=self.m
        p=self.p
        self.A[n,n]=0
        self.B[n,m]=0
        self.c[n,1]=0
        self.A=complete_matrix(self.A)
        self.B=complete_matrix(self.B)
        self.c=complete_matrix(self.c)
    
    def add_variables(self): 
        for t in range(0,self.T+1):
            for i in range(1,self.n+1):
                self.x[i,t]=self.model.addVar(lb=-GRB.INFINITY,ub=GRB.INFINITY,name="x(%d,%d)"%(i,t))
            for i in range(1,self.m+1):
                self.u[i,t]=self.model.addVar(lb=-GRB.INFINITY,ub=GRB.INFINITY,name="u(%d,%d)"%(i,t))
            for i in range(1,self.p+1):
                self.y[i,t]=self.model.addVar(lb=-GRB.INFINITY,ub=GRB.INFINITY,name="y(%d,%d)"%(i,t))
                self.z[i,t]=self.model.addVar(vtype=GRB.BINARY, name="z(%d,%d)"%(i,t))
        self.r=self.model.addVar(lb=-GRB.INFINITY,ub=GRB.INFINITY,name="robustness",obj=-1)
        self.model.update()
        # Dynamics
        for t in range(0,self.T):
            for i in range(1,self.n+1):
                s=LinExpr()
                for j in range(1,self.n+1):
                    s.addTerms(self.A[i,j],self.x[j,t])
                for j in range(1,self.m+1):
                    s.addTerms(self.B[i,j],self.u[j,t])
                self.model.addConstr (self.x[i,t+1]==s + self.c[i,1])
    
    def initial_condition(self,vec):
        for i in range(1,self.n+1):
            self.model.addConstr (self.x[i,0]==vec[i-1])
            
    
    def add_formula(self,string):
        self.formulas[string]="STL formula"
        for t in range(0,self.T+1):
            self.z[string,t]=self.model.addVar(lb=0,ub=1,name="z^%s(%d)"%(string,t))
        self.model.update()

    def integer_encoding(self):
        for t in range(0,self.T+1):
            for i in range(1,self.p+1):
                self.model.addConstr( self.y[i,t] >= self.r - self.M + self.M*self.z[i,t])
                self.model.addConstr( self.y[i,t] <= self.r +  self.M*self.z[i,t])
    
    def add_secondary_signal_state(self,i,vec,g):
        """
        input: 
            vec: coefficients (list), g: constant
        output:
            y=vec * x + g
        """
        for t in range(0,self.T+1):
            s=LinExpr()
            for j in range(1,self.n+1):
                s.addTerms(vec[j-1], self.x[j,t])
            self.model.addConstr( self.y[i,t] == s + g)
        self.formulas[i]="predicate %d"%i
        for j in range(1,self.n+1):
            self.Ex[self.Ex_row,j]=vec[j-1]
            self.Ex[self.Ex_row+1,j]=-vec[j-1]
        self.ex[self.Ex_row]=1
        self.ex[self.Ex_row+1]=1
        self.Ex_row+=2

    def add_secondary_signal_control(self,i,vec,g):
        """
        input: 
            vec: coefficients (list), g: constant
        output:
            y=vec * u + g
        """
        for t in range(0,self.T+1):
            s=LinExpr()
            for j in range(1,self.m+1):
                s.addTerms(vec[j-1], self.u[j,t])
            self.model.addConstr( self.y[i,t] == s + g)
        self.formulas[i]="predicate %d"%i
        for j in range(1,self.m+1):
            self.Fu[self.Fu_row,j]=vec[j-1]
            self.Fu[self.Fu_row+1,j]=-vec[j-1]
        self.fu[self.Fu_row]=1
        self.fu[self.Fu_row+1]=1
        self.Fu_row+=2
    
    def conjunction(self,phi_out,list):
        if not phi_out in self.formulas.keys():
            raise "Error! phi_out not declared as a formula"
        for t in range(0,self.T+1): 
            for f in list:
                self.model.addConstr(self.z[phi_out,t] <= self.z[f,t])

    def disjunction(self,phi_out,list):
        if not phi_out in self.formulas.keys():
            raise "Error! phi_out not declared as a formula"
        for t in range(0,self.T+1): 
            s=LinExpr()
            for f in list:
                s.add(self.z[f,t])
            self.model.addConstr(self.z[phi_out,t] <= s)
            
    def always(self,phi_out,phi_in,interval):
        if not phi_out in self.formulas.keys():
            raise "Error! phi_out not declared as a formula"
        if not phi_in in self.formulas.keys():
            raise "Error! phi_in not declared as a formula"
        for t in range(0,self.T+1-interval[-1]):   
            for tau in interval:    
                self.model.addConstr(self.z[phi_out,t] <= self.z[phi_in,t+tau])
        
    def eventually(self,phi_out,phi_in,interval):
        if not phi_out in self.formulas.keys():
            raise "Error! phi_out not declared as a formula"
        if not phi_in in self.formulas.keys():
            raise "Error! phi_in not declared as a formula"
        for t in range(0,self.T+1-interval[-1]):   
            s=LinExpr()
            for tau in interval:    
                s.add(self.z[phi_in,t+tau])
            self.model.addConstr(self.z[phi_out,t] <= s )    
            
    def solve(self,phi_out):
        self.model.update()
        J=QuadExpr()
        for t in range(0,self.T):
            for j in range(1,self.m+1):
                J.add(self.u[j,t]*self.u[j,t])
#         self.model.addConstr(self.r >= 0 )
        self.model.addConstr(self.z[phi_out,0] >= 1 )
        self.model.setObjective(-1*self.r + 0.00001*J)
        self.model.optimize()
    
    def write_to_file(self):
        f=open("state.txt","w")
        for t in range(0,self.T+1):
            for i in range(1,self.n+1):
                f.write("%0.2f "%self.x[i,t].X)
            f.write("\n")
        f.close()

def show_matrix(X):
    row=0
    column=0
    print "matrix is:",str(X)
    for k in X.keys():
        row=max(row,k[0])
        column=max(column,k[1])
    for i in range(1,row+1):
        for j in range(1,column+1):
            print X[i,j],"  ",
        print "\n"

def complete_matrix(X):
    """
    input: X: sparse matrix
    output: Y: same matrix with zeros completed
    """
    Y={}
    row=0
    column=0
    for k in X.keys():
        row=max(row,k[0])
        column=max(column,k[1])
    for i in range(1,row+1):
        for j in range(1,column+1):
            if (i,j) in X.keys():
                Y[i,j]=X[i,j]
            else:
                Y[i,j]=0
    return Y    