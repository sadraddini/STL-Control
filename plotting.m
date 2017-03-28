clear
clc
close all
X=importdata('state.txt');
[T,n]=size(X);
hold on
rectangle('Position',[3,5,2,2],'FaceColor',[1 0 0])
rectangle('Position',[1,7,1,1],'FaceColor',[0 1 0])
rectangle('Position',[10,10,1,1],'FaceColor',[0 0 1])
% axis([-5 15 -5 15])
grid on
for t=1:T
    plot(X(1:t,1),X(1:t,3),'--','LineWidth',1,'Color',[0 0 1])
    plot(X(1:t,1),X(1:t,3),'o','LineWidth',4,'Color',[1 0 0])
    pause(0.1)
end
hold off