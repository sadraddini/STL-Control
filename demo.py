from STL_control import *
from rci_family import *

s=STL_system(2,1,4)

s.A[1,1]=1
s.A[1,2]=0.5
s.A[2,2]=1

s.B[2,1]=1

s.c[2,1]=0

s.T=10

s.A=complete_matrix(s.A)
s.B=complete_matrix(s.B)
s.c=complete_matrix(s.c)
s.add_variables()

s.add_secondary_signal_state(1,[1,0],-5)
s.add_secondary_signal_state(2,[-1,0],-5)
s.add_secondary_signal_control(3,[1],2.5)
s.add_secondary_signal_control(4,[-1],2.5)

s.add_formula("phi_1")
s.add_formula("phi_2")
s.add_formula("phi_3")
s.add_formula("phi_4")
s.add_formula("phi_5")

s.eventually("phi_1",1,range(0,10))
s.eventually("phi_2",2,range(0,10))
s.always("phi_3",3,range(0,10))
s.always("phi_4",4,range(0,10))

s.conjunction("phi_5",["phi_1","phi_2","phi_3","phi_4"])

s.initial_condition([0,0])
s.solve("phi_5")
 
for t in range(0,s.T):
    print t,"x1:",s.x[1,t].X," x2:",s.x[2,t].X, "u:", s.u[1,t].X
