import pyxel, math

world = {} # The empty dict that will contain the world
charges = ['+', '-']
charge_cols = {'+': 8, '-': 12, 'neutral': 13}
# The colors for the areas that are charged ^
WORLD_SIZE = 50
SCALE = 5

for x in range(WORLD_SIZE):
    for y in range(WORLD_SIZE):
        world[(x, y)] = charges[0] if pyxel.noise(x/SCALE, y/SCALE)+1 < 1 else charges[1]
world[(0,0)] = 'neutral' # The finish zone
GRID_SIZE = 100 # The size of each tile on the grid in pixels
RENDER_DIST = 10

MAGNET_FORCE = 100
MAX_DIST = 100 #math.log(0.1/MAGNET_FORCE, 0.9)

pos = [(0,0),(1,0),(2,0),(3,0),
       (0,1),(1,1),(2,1),(3,1),
       (0,2),(1,2),(2,2),(3,2),
       (0,3),(1,3),(2,3),(3,3)
    ]

def distance(x1, y1, x2, y2):
    return pyxel.sqrt((x2-x1)**2+(y2-y1)**2)

class Player:
    def __init__(self, x, y, charge):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.friction = 0.1
        self.charge = charge
        self.positive = True if charge == '+' else False
    def update(self, world):
        if pyxel.btn(pyxel.KEY_W):
            self.dy -= 1
        if pyxel.btn(pyxel.KEY_S):
            self.dy += 1
        if pyxel.btn(pyxel.KEY_A):
            self.dx -= 1
        if pyxel.btn(pyxel.KEY_D):
            self.dx += 1
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.positive = not self.positive
            self.charge = '+' if self.positive else '-'
        for w, c in world.items():
            d = distance(self.x*GRID_SIZE,
                self.y*GRID_SIZE, (w[0]+0.5)*GRID_SIZE, (w[1]+0.5)*GRID_SIZE)
            if d <= MAX_DIST*GRID_SIZE and c == self.charge:
                # Calculate and apply magnetic force
                force = MAGNET_FORCE * (0.9**d)
                n = pyxel.sqrt((self.x-w[0])**2+(self.y-w[1])**2)+0.01
                fx = ((self.x-w[0])/n)*force
                fy = ((self.y-w[1])/n)*force
                self.dx += fx
                self.dy += fy
        self.x += self.dx/50
        self.y += self.dy/50
        self.x = min(max(self.x, 0), WORLD_SIZE)
        self.y = min(max(self.y, 0), WORLD_SIZE)
        if self.x == 0 or self.x == WORLD_SIZE:
            self.dx = 0
        if self.y == 0 or self.y == WORLD_SIZE:
            self.dy = 0
        self.dx *= 1-self.friction
        self.dy *= 1-self.friction
        #text(0, 20, str(d), 7)
    def update_without_keys(self):
        self.x += self.dx/50
        self.y += self.dy/50
        self.x = min(max(self.x, 0), WORLD_SIZE)
        self.y = min(max(self.y, 0), WORLD_SIZE)
        if self.x == 0 or self.x == WORLD_SIZE:
            self.dx = 0
        if self.y == 0 or self.y == WORLD_SIZE:
            self.dy = 0
        self.dx *= 1-self.friction
        self.dy *= 1-self.friction
    def draw(self):
        pyxel.circ(400, 300, 15, charge_cols[self.charge])
        pyxel.circb(400, 300, 15, 0)

ws_1 = WORLD_SIZE-1
imgs = [pyxel.Image(800, 600) for _ in range(8)]
##for i in range(16):
imgs[0].load(0,0, 'title.png')
#imgs[0].load(0,0,'title.png')
#imgs[1].load(0,0,'win.png')
for i in range(1, 8):
    imgs[i].load(0,0,'s-0'+str(i+1)+'.png')
##    for a in range(1, 16):
##        imgs[i].load(pos[a][0]*200,pos[a][1]*150,'i'+str(i+1)+'/s_'+('0' if len(str(a+1)) == 1 else '')+str(a+1)+'.gif')

def draw_world(p, w):
    for x in range(WORLD_SIZE):
        for y in range(WORLD_SIZE):
            if pyxel.sqrt((p.x-x)**2+(p.y-y)**2) <= RENDER_DIST:
                pyxel.rect((x-p.x)*GRID_SIZE+400,
                     (y-p.y)*GRID_SIZE+300, GRID_SIZE,
                     GRID_SIZE, charge_cols[world[(x, y)]])

state = 'title'
seed = pyxel.rndi(1, 101)

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def round_to_nearest_prime(num):
    num = round(num)
    if num <= 2:
        return 2
    if is_prime(num):
        return num
    lower = num - 1
    upper = num + 1
    while True:
        lower_prime = is_prime(lower)
        upper_prime = is_prime(upper)
        if lower_prime and upper_prime:
            return [lower, upper]
        if lower_prime:
            return lower
        if upper_prime:
            return upper
        lower -= 1
        upper += 1

seed = round_to_nearest_prime(seed)
if type(seed) == list:
    seed = seed[0]

player = Player(ws_1, ws_1,
                charges[(charges.index(world[(ws_1,ws_1)])+1)%1])

def update():
    global state, slide
    if state == 'title':
        global player
        if pyxel.btnp(pyxel.KEY_RETURN):
            state = 'game'
            player = Player(ws_1, ws_1,
                            charges[(charges.index(world[(ws_1,ws_1)])+1)%1])
        if pyxel.btn(pyxel.KEY_SPACE):
            state = 'tutorial'
            slide = 0
    if state == 'game':
        player.update(world)
        if player.x < 1 and player.y < 1:
            state = 'winner'
    if state == 'winner':
        if pyxel.btnp(pyxel.KEY_RETURN):
            state = 'title'
            seed = pyxel.rndi(1, 101)
            seed = round_to_nearest_prime(seed)
            if type(seed) == list:
                seed = seed[0]
            pyxel.nseed(seed)
            for x in range(WORLD_SIZE):
                for y in range(WORLD_SIZE):
                    world[(x, y)] = charges[0] if pyxel.noise(x/SCALE, y/SCALE)+1 < 1 else charges[1]
            world[(0,0)] = 'neutral' # The finish zone
        player.update_without_keys()
    if state == 'tutorial':
        # A series of slides containing the key terms
        if pyxel.btnp(pyxel.KEY_RETURN):
            slide += 1
        if slide > 5:
            state = 'title'

def draw():
    global state, slide
    pyxel.cls(0)
    if state == 'game':
        draw_world(player, world)
        player.draw()
        #text(0, 0, str(player.x)+', '+str(player.y), 7)
        #text(0, 10, str(MAX_DIST*GRID_SIZE), 7)
    if state == 'winner':
        draw_world(player, world)
        player.draw()
        pyxel.blt(0,0,imgs[1],0,0,800,600,colkey=0)
    if state == 'title':
        #text(378, 0, 'Magnet Maze', 7)
        pyxel.blt(0,0,imgs[0],0,0,800,600,colkey=0)
    if state == 'tutorial':
        # Display the slide (might add interactive slides later)
        pyxel.blt(0,0,imgs[slide+2],0,0,800,600,colkey=0)
    pyxel.flip()

pyxel.init(800, 600, 'Magnet Maze', fps=50)
pyxel.run(update, draw)
