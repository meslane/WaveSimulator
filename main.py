import pygame
import numpy as np
import math

v = 1 #speed of wave
t = 1 #simulation time step in seconds
h = 1 #grid distance step in meters

k = v * (t/h) #k value for boundary conditions

damping = 0.95

grid_dim = (3, 100, 100) #size of simulation grid

u = np.zeros(grid_dim) #simulation grid
#u[1][50][50] = 1

for i in range(40,60): #plane wave radiation
    u[1][i][10] = 1

for i in range(100):
    u[0][i][75] = 1000

'''
for i in range(75):
    u[0][0][i] = 1000
    u[0][99][i] = 1000
'''

u[0][49][75] = 0 #make slit
u[0][50][75] = 0

#u[0][44][75] = 0
#u[0][48][75] = 0
#u[0][52][75] = 0
#u[0][56][75] = 0

'''
stencil = [[0, 1, 0],
           [1, -4, 1],
           [0, 1, 0]]
'''

stencil = [[0.25, 0.5, 0.25],
           [0.5, -3, 0.5],
           [0.25, 0.5, 0.25]]

def value_to_color(val):
    if (val == 0):
        return 0 #will give domain error otherwise
    elif (val == 1000):
        return (255,255,255) #draw barrier
    
    log_val = int(50 * math.log(abs(val), 10))
    
    if (log_val < -255):
        return (0,0,0)
    elif (log_val >= 1):
        log_val = 0
        
    if (val > 0):
        return (0, 0, 255 + log_val)
    else:
        return (255 + log_val, 0, 0)
        
def tick(u, t, v, h):
    #update values
    u[2] = u[1]
    u[1] = u[0]

    for y in range(0, grid_dim[2]):
        for x in range(0, grid_dim[1]):
            if u[1][x][y] != 1000: #if not barrier
                if (x > 0) and (x < (grid_dim[1] - 1)) and (y > 0) and (y < (grid_dim[2] - 1)): #if not radiating boundary
                    stencil_sum = 0 #perform stencil convolution
                    
                    for j in range(3):
                        for i in range(3):
                            if (u[1][x + (i-1)][y + (j-1)] != 1000): #if not barrier
                                stencil_sum += (u[1][x + (i-1)][y + (j-1)] * stencil[i][j])
                                
                    stencil_sum *= (((t * v) / h) ** 2.0) #apply scalar
                    
                    stencil_sum += 2 * u[1][x][y] #add initial conditions
                    stencil_sum -= u[2][x][y]
                    
                    u[0][x][y] = stencil_sum
                    u[0][x][y] *= damping #damping
                else: #if radiating boundary
                    c = np.zeros(3)
                    if x == 0:
                        c[0] = u[1][1][y]
                        c[1] = u[0][1][y]
                        c[2] = u[1][0][y]
                    elif x == (grid_dim[1] - 1):
                        c[0] = u[1][grid_dim[1] - 2][y]
                        c[1] = u[0][grid_dim[1] - 2][y]
                        c[2] = u[1][grid_dim[1] - 1][y]
                    elif y == 0:
                        c[0] = u[1][x][1]
                        c[1] = u[0][x][1]
                        c[2] = u[1][x][0]
                    elif y == (grid_dim[1] - 1):
                        c[0] = u[1][x][grid_dim[1] - 2]
                        c[1] = u[0][x][grid_dim[1] - 2]
                        c[2] = u[1][x][grid_dim[1] - 1]
                    
                    for i in range(3):
                        if c[i] == 1000:
                            c[i] = 0
                    
                    u[0][x][y] = c[0] + (k - 1)/(k + 1) * (c[1] - c[2])

def main():
    pygame.init()
    
    pygame.display.set_caption("Wave Simulation")
    window = pygame.display.set_mode((grid_dim[1], grid_dim[2]), pygame.RESIZABLE)
    screen = pygame.Surface((grid_dim[1], grid_dim[2]))
    
    run = True
    while run == True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        tick(u, t, v, h) #tick
                
        for y in range(grid_dim[2]):
            for x in range(grid_dim[1]):
                try:
                    screen.fill(value_to_color(u[0][x][y]), ((x,y), (1, 1))) #draw single pixel
                except ValueError:
                    print(value_to_color(u[0][x][y]))
                    exit()
                    
        window.blit(pygame.transform.scale(screen, window.get_rect().size), (0, 0))
        pygame.display.flip()

main()