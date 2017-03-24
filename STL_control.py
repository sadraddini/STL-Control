"""
Here we synthesize controllers from STL
Sadra Sadraddini
"""
M=100

from gurobipy import *
import random

class system:
	def __init__(self):
		self.model=Model("STL_Spec")
		self.x={}
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
				self.y[i,t]=self.model.addVar(lb=-GRB.INFINITY,ub=GRB.INFINITY,name="z(%d,%d)"%(i,t))
				self.z[i,t]=self.model.addVar(vtype=GRB.BINARY, name="z(%d,%d)"%(i,t))
		self.model.update()
		# predicates are formulas!
		for i in range(1,self.p+1):
			self.formulas[i]={}
			for t in range(0,self.T+1):
				self.formulas[i][t]=self.model.addVar(lb=0,ub=1,name="predicate(%d,%d)"%(i,t))
				self.model.update()
				self.model.addConstr (self.formulas[i][t]==self.y[i,t])
		
			
	def add_formula(self,string):
		self.formulas[string]={}
		for t in range(0,self.T+1):
			self.formulas[string][t]=self.model.addVar(lb=0,ub=1,name="z^%s(%d)"%(string,t))
		self.model.update()

			
		
	
	def integer_encoding(self):
		for k in self.y.keys():
			self.model.addConstr ( self.y[k] >= - M + M * self.z[k])
			self.model.addConstr ( self.y[k] <=	  M * self.z[k])
	
	def add_secondary_signal_state(i,list1,list2,g):
		"""
		input: 
			list1: indices of state
			list 2: repsective coefficients
			g: constant
		output:
			y=list 2 * x + g
		"""
		s=LinExpr()
		for t in range(0,self.T+1):
			for j in list1:
				s.addTerms(self.list2[j], self.x[j,t])
			self.model.addConstr( self.y[i,t]== s + g)

	def add_secondary_signal_control(i,list1,list2,g):
		"""
		input: 
			list1: indices of controls
			list 2: repsective coefficients
			g: constant
		output:
			y=list 2 * u + g > 0
		"""
		s=LinExpr()
		for t in range(0,self.T+1):
			for j in list1:
				s.addTerms(self.list2[j], self.u[j,y])
			self.model.addConstr( self.y[i,t]== s + g)
	
	def conjunction(self,phi_out,list):
		if not phi_out in self.formulas.keys():
			raise "Error! phi_out not declared as a formula"
		for f in list:
			s=LinExpr()
			for t in range(0,self.T+1): 
				self.model.addConstr(z[phi_out][t] <= z[f][t])
				s.add(z[f][t])
			self.model.addConstr(z[phi_out][t] >= s - len(list) + 1 )

	def disjunction(self,phi_out,list):
		if not phi_out in self.formulas.keys():
			raise "Error! phi_out not declared as a formula"
		for f in list:
			s=LinExpr()
			for t in range(0,self.T+1): 
				self.model.addConstr(z[phi_out][t] >= z[f][t])
				s.add(z[f][t])
			self.model.addConstr(z[phi_out][t] <= s)
			
	def always(self,phi_out,phi_in,interval):
		if not phi_out in self.formulas.keys():
			raise "Error! phi_out not declared as a formula"
		if not phi_in in self.formulas.keys():
			raise "Error! phi_in not declared as a formula"
		for t in range(0,self.T+1-interval[len(interval)-1]):	
			s=LinExpr()
			for tau in interval:	
				self.model.addConstr(z[phi_out][t] <= z[phi_in][tau])
				s.add(z[phi_in][tau])
			self.model.addConstr(z[phi_out][t] >= s - len(interval) + 1 )		
		
	def eventually(self,phi_out,phi_in,interval):
		if not phi_out in self.formulas.keys():
			raise "Error! phi_out not declared as a formula"
		if not phi_in in self.formulas.keys():
			raise "Error! phi_in not declared as a formula"
		for t in range(0,self.T+1-interval[len(interval)-1]):	
			s=LinExpr()
			for tau in interval:	
				self.model.addConstr(z[phi_out][t] >= z[phi_in][tau])
				s.add(z[phi_in][tau])
			self.model.addConstr(z[phi_out][t] <= s )		
		