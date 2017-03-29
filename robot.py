from STL_control import *
from rci_family import *

s=STL_system(4,2,16)

s.matrix_installation()

s.A[1,1]=1
s.A[1,2]=1
s.A[2,2]=1
s.A[3,3]=1
s.A[3,4]=1
s.A[4,4]=1


s.B[2,1]=1
s.B[4,2]=1


s.T=25


s.add_variables()		 

s.add_secondary_signal_state(1,[0,0,-1,0],4)	# -y+4>0 --> 4>y
s.add_secondary_signal_state(2,[1,0,0,0],-7)	# x-7>0 --> x>7
s.add_secondary_signal_state(3,[0,0,1,0],-8)	# y-8>0 --> y>8
s.add_secondary_signal_state(4,[-1,0,0,0],3)	# -x+3>0 --> 3>x

s.add_secondary_signal_state(5,[0,0,1,0],-10)	# y-10>0 --> y>10
s.add_secondary_signal_state(6,[-1,0,0,0],11)	#-x+11>0 --> 11>x
s.add_secondary_signal_state(7,[0,0,-1,0],11)	# -y+11>0 --> 11>y
s.add_secondary_signal_state(8,[1,0,0,0],-10)	# x-10>0 --> x>10

s.add_secondary_signal_state(9,[1,0,0,0],-1)	# x-1>0 --> x>1
s.add_secondary_signal_state(10,[-1,0,0,0],2)	# -x+2>0 --> 2>x
s.add_secondary_signal_state(11,[0,0,1,0],-7)	# y-7>0 --> y>7
s.add_secondary_signal_state(12,[0,0,-1,0],8)	# -y +8 > 0 --> 8>y

s.add_secondary_signal_control(13,[1,0],1)	  # u+100>0 --> u>-100
s.add_secondary_signal_control(14,[-1,0],1)	  # -u+100>0 --> 100>u
s.add_secondary_signal_control(15,[0,1],1)
s.add_secondary_signal_control(16,[0,-1],1)

s.add_formula("obstacle")
s.disjunction("obstacle",[1,2,3,4])
s.add_formula("discover")
s.conjunction("discover",[5,6,7,8])
s.add_formula("upload")
s.conjunction("upload",[9,10,11,12])
s.add_formula("controls")
s.conjunction("controls",[13,14,15,16])

s.add_formula("phi_1")
s.always("phi_1","obstacle",range(0,s.T))
s.add_formula("phi_2")
s.eventually("phi_2","discover",range(0,20))
s.add_formula("phi_3")
s.eventually("phi_3","upload",range(20,s.T))
s.add_formula("phi_4")
s.always("phi_4","controls",range(0,s.T))

s.add_formula("phi_whole")
s.conjunction("phi_whole",["phi_1","phi_2","phi_3","phi_4"])

s.initial_condition([0,0,0,0])
s.integer_encoding()
# s.solve("phi_whole")
# s.write_to_file()
# 
# print "robustness was",s.r.X
# for t in range(0,s.T):
#	  print t,"x:",s.x[1,t].X,"vx:",s.x[2,t].X," y:",s.x[3,t].X,"vy:",s.x[4,t].X, "ux:", s.u[1,t].X, "uy:", s.u[2,t].X
#	  print t, "z upload", s.z["upload",t].X, "z obstacle", s.z["obstacle",t].X, "z discover", s.z["discover",t].X
#	  print "\n"
	
"""
Here I start computing the tube!
Then we will add the tube to the nominal trajectory
"""
tube=system()
tube.n=s.n # number of variables
tube.m=s.m # number of controls
tube.K=10 # Design variable, degree
tube.nW=8 # Number of dis set rows
tube.nX=24 # rows of X, rows of H
tube.nU=8 # rows of U, rows of P
tube.A=s.A
tube.B=s.B
tube.F={}
tube.g={}
scale_w=0.2
for i in range(1,s.n+1):
	tube.F[2*i-1,i]=1
	tube.F[2*i,i]=-1
	tube.g[2*i-1]=1*scale_w
	tube.g[2*i]=1*scale_w
tube.F=complete_matrix(tube.F)

tube.H=s.Ex
tube.r=s.ex
tube.P=s.Fu
tube.q=s.fu

tube.compute_AA()
tube.compute_HAB()
tube.compute_FAB()

for i in range(1,tube.n+1):
	tube.mu[i]=0

for j in range(1,tube.m+1):
	tube.v[j]=0
		
		
tube.RCI()
tube.compute_D()
print "beta is",tube.beta
print "gamma is",tube.gamma

f=open("tube_state.txt","w")
tube.x=tube.mu
for t in range(0,s.T+1):
	for i in range(1,tube.n+1):
		f.write("%0.2f "%tube.x[i])
	f.write("\n")	
	tube.RCI_control(tube.x)
	tube.evolve()
f.close()
	
	
	
	