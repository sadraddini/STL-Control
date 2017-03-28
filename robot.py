from STL_control import *
from rci_family import *

s=STL_system(4,2,16)

obj=s.model.getObjective()
print obj

s.A[1,1]=1
s.A[1,2]=1
s.A[2,2]=1
s.A[3,3]=1
s.A[3,4]=1
s.A[4,4]=1


s.B[2,1]=1
s.B[4,2]=1

s.c[2,1]=0
s.c[4,1]=0


s.T=40

s.A=complete_matrix(s.A)
s.B=complete_matrix(s.B)
s.c=complete_matrix(s.c)

show_matrix(s.A)
show_matrix(s.B)
show_matrix(s.c)

s.add_variables()        

s.add_secondary_signal_state(1,[0,0,-1,0],5)    # -y+5>0 --> 5>y
s.add_secondary_signal_state(2,[1,0,0,0],-5)    # x-5>0 --> x>5
s.add_secondary_signal_state(3,[0,0,1,0],-7)    # y-7>0 --> y>7
s.add_secondary_signal_state(4,[-1,0,0,0],3)    # -x+3>0 --> 3>x

s.add_secondary_signal_state(5,[0,0,1,0],-10)   # y-10>0 --> y>10
s.add_secondary_signal_state(6,[-1,0,0,0],11)   #-x+11>0 --> 11>x
s.add_secondary_signal_state(7,[0,0,-1,0],11)   # -y+11>0 --> 11>y
s.add_secondary_signal_state(8,[1,0,0,0],-10)   # x-10>0 --> x>10

s.add_secondary_signal_state(9,[1,0,0,0],-1)    # x-1>0 --> x>1
s.add_secondary_signal_state(10,[-1,0,0,0],2)   # -x+2>0 --> 2>x
s.add_secondary_signal_state(11,[0,0,1,0],-7)   # y-7>0 --> y>7
s.add_secondary_signal_state(12,[0,0,-1,0],8)   # -y +8 > 0 --> 8>y

s.add_secondary_signal_control(13,[1,0],100)    # u+100>0 --> u>-100
s.add_secondary_signal_control(14,[-1,0],100)   # -u+100>0 --> 100>u
s.add_secondary_signal_control(15,[0,1],100)
s.add_secondary_signal_control(16,[0,-1],100)

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

s.initial_condition([2,0,0,0])
s.solve("phi_whole")
s.write_to_file()

print "robustness was",s.r.X
for t in range(0,s.T):
    print t,"x:",s.x[1,t].X,"vx:",s.x[2,t].X," y:",s.x[3,t].X,"vy:",s.x[4,t].X, "ux:", s.u[1,t].X, "uy:", s.u[2,t].X
    print t, "z upload", s.z["upload",t].X, "z obstacle", s.z["obstacle",t].X, "z discover", s.z["discover",t].X
    print "\n"