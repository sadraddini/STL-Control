clear
clc
close all
X=importdata('state.txt');
X_tube=importdata('tube_state.txt');
[T,n]=size(X);
X_real=X+X_tube;

V=importdata('tube_vertices.txt');

[K] = convhull(V(:,1),V(:,3));

figure
hold on
set(gcf,'Units','inches',...
 'Position',[20 5 10 10])
set(0,'defaultaxesposition',[0 0 1 1])
rectangle('Position',[3,4,4,4],'FaceColor',[1 0 0])
rectangle('Position',[1,7,1,1],'FaceColor',[0 1 0])
rectangle('Position',[10,10,1,1],'FaceColor',[0 0 1])
% axis([-5 15 -5 15])
grid minor
axis('equal')
plot(X(:,1),X(:,3),'--','LineWidth',1,'Color',[0 0 1])
plot(X(:,1),X(:,3),'o','LineWidth',4,'Color',[1 0 0])


pause(0.5)
for t=1:T
    fill(V(K,1)+X(t,1),V(K,3)+X(t,3),[1 0.8 0.8])
    alpha(.5)
    plot(X_real(1:t,1),X_real(1:t,3),'LineWidth',2,'Color',[0.2 0.5 0.2])
    plot(X_real(1:t,1),X_real(1:t,3),'o','LineWidth',4,'Color',[0.5 0.2 0.2])
    pause(0.1)
end
hold off