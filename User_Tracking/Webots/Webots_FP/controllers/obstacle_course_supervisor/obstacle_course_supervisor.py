# this file controls all the obstacle movement in the webots world
from controller import Supervisor

obstacle_mover = Supervisor()

time_step = 50
i = 0
# initialize all objects to be controlled by the supervisor here and get translation field
ped_2_node = obstacle_mover.getFromDef('Ped_2')
ped_3_node = obstacle_mover.getFromDef('Ped_3')
tesla = obstacle_mover.getFromDef('Tesla')

ped2_T_field = ped_2_node.getField('translation')
ped3_T_field = ped_3_node.getField('translation')
tesla_T_field = ped_3_node.getField('translation')

# initial object positions
ped_2_pos = ped_2_node.getPosition()
ped_3_pos = ped_3_node.getPosition()

print(ped_2_pos)


ped_velocity = 1 # m/s
while obstacle_mover.step(time_step) != -1:
    # set position changes here
    # define periodic linear trajectory for all objects
    ped_2_pos = [ped_velocity*i/1000+ped_2_pos[0], ped_2_pos[1], ped_2_pos[2]]
    ped2_T_field.setSFVec3f(ped_2_pos)

    i+=1
