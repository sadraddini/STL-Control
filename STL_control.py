"""
Here we synthesize controllers from STL
Sadra Sadraddini
"""
M=100

from gurobipy import *
import random

class STL_system:
	def __init__(self):
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
		self.E={}
		self.F={}
		self.g={}
		self.formulas={} #key: name, val: dictionary of t variables
		
	
	def add_variables(self): 
		for t in range(0,self.T+1):
			for i in range(1,self.n+1):
				self.x[i,t]=self.model.addVar(lb=-GRB.INFINITY,ub=GRB.INFINITY,name="x(%d,%d)"%(i,t))
			for i in range(1,self.m+1):
				self.u[i,t]=self.model.addVar(lb=-GRB.INFINITY,ub=GRB.INFINITY,name="u(%d,%d)"%(i,t))
			for i in range(1,self.p+1):
				self.y[i,t]=self.model.addVar(lb=-GRB.INFINITY,ub=GRB.INFINITY,name="y(%d,%d)"%(i,t))
				self.z[i,t]=self.model.addVar(vtype=GRB.BINARY, name="z(%d,%d)"%(i,t))
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
	
	def add_formula(self,string):
		self.formulas[string]="STL formula"
		for t in range(0,self.T+1):
			self.z[string,t]=self.model.addVar(lb=0,ub=1,name="z^%s(%d)"%(string,t))
		self.model.update()

	def integer_encoding(self):
		for k in self.y.keys():
			self.model.addConstr ( self.y[k] >= - M + M * self.z[k])
			self.model.addConstr ( self.y[k] <=	  M * self.z[k])
	
	def add_secondary_signal_state(self,i,vec,g):
		"""
		input: 
			vec: coeffieicents (list), g: constant
		output:
			y=vec * x + g
		"""
		for t in range(0,self.T+1):
			s=LinExpr()
			for j in range(1,self.n+1):
				s.addTerms(vec[j-1], self.x[j,t])
			self.model.addConstr( self.y[i,t]== s + g)
		self.formulas[i]="predicate %d"%i

	def add_secondary_signal_control(self,i,vec,g):
		"""
		input: 
			vec: coeffieicents (list), g: constant
		output:
			y=vec * u + g
		"""
		for t in range(0,self.T+1):
			s=LinExpr()
			for j in range(1,self.m+1):
				s.addTerms(vec[j-1], self.u[j,t])
			self.model.addConstr( self.y[i,t]== s + g)
		self.formulas[i]="predicate %d"%i
	
	def conjunction(self,phi_out,list):
		if not phi_out in self.formulas.keys():
			raise "Error! phi_out not declared as a formula"
		for t in range(0,self.T+1): 
			for f in list:
				s=LinExpr()
				self.model.addConstr(self.z[phi_out,t] <= self.z[f,t])
				s.add(self.z[f,t])
			self.model.addConstr(self.z[phi_out,t] >= s - len(list) + 1 )

	def disjunction(self,phi_out,list):
		if not phi_out in self.formulas.keys():
			raise "Error! phi_out not declared as a formula"
		for t in range(0,self.T+1): 
			for f in list:
				s=LinExpr()
				self.model.addConstr(self.z[phi_out,t] >= self.z[f,t])
				s.add(self.z[f,t])
			self.model.addConstr(self.z[phi_out,t] <= s)
			
	def always(self,phi_out,phi_in,interval):
		if not phi_out in self.formulas.keys():
			raise "Error! phi_out not declared as a formula"
		if not phi_in in self.formulas.keys():
			raise "Error! phi_in not declared as a formula"
		for t in range(0,self.T+1-interval[len(interval)-1]):	
			s=LinExpr()
			for tau in interval:	
				self.model.addConstr(self.z[phi_out,t] <= self.z[phi_in,tau])
				s.add(self.z[phi_in,tau])
			self.model.addConstr(self.z[phi_out,t] >= s - len(interval) + 1 )	   
		
	def eventually(self,phi_out,phi_in,interval):
		if not phi_out in self.formulas.keys():
			raise "Error! phi_out not declared as a formula"
		if not phi_in in self.formulas.keys():
			raise "Error! phi_in not declared as a formula"
		for t in range(0,self.T+1-interval[len(interval)-1]):	
			s=LinExpr()
			for tau in interval:	
				self.model.addConstr(self.z[phi_out,t] >= self.z[phi_in,tau])
				s.add(self.z[phi_in,tau])
			self.model.addConstr(self.z[phi_out,t] <= s )	 
			
	def solve(self,phi_out):
		self.model.addConstr(self.z[phi_out,0] == 1 )
		self.model.optimize()  
		  

def show_matrix(X):
	row=0
	column=0
	for k in X.keys():
		row=max(row,k[0])
		column=max(column,k[1])
	for i in range(1,row+1):
		for j in range(1,column+1):
			print X[i,j],"	",
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