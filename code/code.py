class CA_g:
    """
    Cellular automata
    Spatial parameters: w,l,h
    Cell list
    """
    def __init__(self,W,L,H,g,m):
        self.W,self.L,self.H = W,L,H
        self.cell_flag = np.zeros((W+1,L+1,H+1))
        self.cell = {}
        self.cells = []
        self.G = g
        self.i = 0
        self._init_cell(m)

    def _init_cell(self,m):
        SAND_NUM = 0
        WATER_NUM = 0
        EMPTY_NUM = 0
        # UP2DOWN = 0
        # ca = CA(W,L,H)

        # Initialize the cells inside the geometry
        for i in (range(self.W+1)):
            for j in range(self.L+1):
                if self.G.x_y_is_out(i,j):
                    continue
                
                for k in range(self.H+1):
                    if i == 40 and j == 20 and k == 0:
                        pass
                    P = np.array([i,j,k])
                    if self.G.is_outside(P):
                        continue
                    # if k> P_0[2]+h_tai:
                    # break
                    
                    region = None
                    if k<=self.G.H_base:
                        region = DOWN
                    else:
                        region = UP

                    cell_ = sample_cell(m,loc=[i,j,k],region = region)

                    # M_EMPTY probability is directly set to empty cells
                    if np.random.rand()<M_EMPTY:
                        EMPTY_NUM +=1
                        cell_.type = EMPTY

                    else:
                        if cell_.type == SAND:
                            SAND_NUM +=1
                        else:
                            WATER_NUM +=1
                        
                    self.insert_cell((i,j,k),cell_)
        self.N0 = self.get_N_up() # Initial number of upper cells
        printt(f'{self.G.name} Cell System: Initialization completed, SAND:{SAND_NUM},WATER:{WATER_NUM},EMPTY:{EMPTY_NUM}; Initial number of non-empty cells in the upper part: {self.N0}')
    def insert_cell(self,i,cell):
        self.cell[i] = cell
        self.cells.append(cell)
        self.cell_flag[i] = 1
    def get_cell(self,i):
        if self.cell_flag[i] == 0:
            return False
        else:
            return self.cell[i]
    
    def get_neiborhood(self,cell,rule=None):
        x,y,z = cell.x,cell.y,cell.z
        n = []
        w_n = 0
        s_n = 0
        e_n = 0
        P=[]
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    if not (i==0 and j ==0 and k ==0):
                        xdot,ydot,zdot = x+i-1,y+j-1,z+k-1
                        if not (0<=xdot<=self.W and 0<=ydot<=self.L and 0<=zdot<=self.H):
                            e_n+=1
                            continue
                        cj = self.get_cell((xdot,ydot,zdot))
                        if cj is False:
                            e_n+=1
                            continue
                        if cj.type==SAND:
                            s_n+=1
                        elif cj.type == WATER:
                            w_n +=1
                        else:
                            e_n+=1
                        p=1
                        if rule =='sand':
                            if cj.type == SAND:
                                p=0
                            else:
                                if z>self.G.H_base:
                                    if k-1<0:# down
                                        p*=alpha
                                    elif k-1 == 0 :# same layer
                                        p*=(1-alpha)
                                    else:
                                        p*=0

                                    if cj.type == EMPTY: # Towards the empty cell
                                        p*=beta
                                    elif cj.type == WATER :# towards the water cell
                                        p*=(1-beta)
                                else:
                                    p=0
                        elif rule =='water':
                            if cj.type == SAND or cj.type == WATER:
                                p = 0
                            else:
                                if k-1<0:# down
                                        p*=alpha
                                elif k-1 == 0 :# same layer
                                    p*=(1-alpha)
                                else:
                                    p*=0
                                

                        else:
                            p=0
                        P.append(p)
                        n.append(cj)
                        
                                
        P = np.array(P)
        swap_flag = np.sum(P)>0
        if np.sum(P)>0:
            def guiyi(p):
                return p/np.sum(p)
            P = guiyi(P)

        return n,w_n,s_n,e_n,P,swap_flag
    def get_unstable_degree(self,cell,rule=None):
        n,w_n,s_n,e_n,P,swap_flag = self.get_neiborhood(cell,rule)
        if rule =='sand':
            water_factor = a if w_n> W0 else -a 
# print()
        return water_factor*w_n+b*e_n-c*s_n
    def get_N_down(self):
        N = 0
        for ci in self.cells:
            x,y,z = ci.loc
            if z<=self.G.H_base:
                P = np.array([x,y,z])
                if ci.type != EMPTY:
                    N+=1
        return N
    def get_N_up(self):
        N = 0
        for ci in self.cells:
            x,y,z = ci.loc
            if z> self.G.H_base:
                # P = np.array([x,y,z])
                if ci.type != EMPTY:
                    N+=1
        return N


    def xiashen(self):
        x0,y0,z0 = self.G.conf['P_0']
        
        # Water seepage down
        N_xiasheng = 0
        for ci in self.cells:
            h = ci.z
            if h <=self.G.H_base:
                if ci.type == WATER:
                    rand = np.random.rand()
                    if rand <(1-h/self.G.H_base)*SHENGSHUI:
                        N_xiasheng+=1
                        type_change(ci,EMPTY,(1-h/self.G.H_base)*SHENGSHUI,'infiltration')
        printt(f'Water seepage down {N_xiasheng} cells')

    def xiayu(self):
        # Rain
        N_sandjian = 0
        N_rainempty = 0
        for RAINI in range(YUSHUIQIANGDU):
            for ci in self.cells:
                x,y,z = ci.loc
                P = np.array([x,y,z])
                if self.G.is_on(P) and ZUOYONGCEMIAN:
                    if ci.type == EMPTY:
                        if np.random.rand()<PRAIN_EMPTY_REPLACE:
                            type_change(ci,WATER,PRAIN_EMPTY_REPLACE,'rain replace empty cells')
                            N_rainempty+=1
                    elif ci.type == SAND:
                        if np.random.rand()<PRAIN_SAND_REPLACE:
                            type_change(ci,WATER,PRAIN_SAND_REPLACE,'rain splashing sand')
                            N_sandjian+=1
                if z == self.G.z0 + self.G.h_tai and ZUOYONGDINGMIAN:
                    if ci.type == EMPTY:
                        if np.random.rand()<PRAIN_EMPTY_REPLACE:
                            type_change(ci,WATER,PRAIN_EMPTY_REPLACE,'rain replace empty cells')
                            N_rainempty+=1
                    elif ci.type == SAND:
                        if np.random.rand()<PRAIN_SAND_REPLACE:
                            type_change(ci,WATER,PRAIN_SAND_REPLACE,'rain splashing sand')
                            N_sandjian+=1
                
        printt(f'Rain replaces {N_rainempty} cells, rain splashes sand {N_sandjian}')
    def zhengfa(self):
        # Evaporation
        N_zhengfa = 0
        for zi in np.arange(z0+h_tai+1):
            if zi >self.G.H_base: # The outer surface of the upper part
                for xi in np.arange(x0-l_wave/2,x0+l_wave/2+1):
                    # rdot = (H_total-zi+z0)*R_di/H_total
                    # find = EMPTY
                    y_delta = self.G.get_y_range(xi=xi,zi=zi)
                    for yi in np.arange(y0-y_delta,y0+y_delta+1):
                        xi,yi,zi = int(xi),int(yi),int(zi)
                        # print([xi,yi,zi])
                        if self.G.is_inside(np.array([xi,yi,zi])) or self.G.is_on(np.array([xi,yi,zi])):
                            cj = self.get_cell((xi,yi,zi))
                            assert cj is not False
                            if cj is not False:
                                if cj.type == EMPTY:
                                    pass
                                elif cj.type == SAND:
                                    # There is a grain of sand blocking this direction
                                    break
                                else:
                                    # Find a drop of water on the outer surface
                                    x,y,z = cj.loc
                                    P = np.array([x,y,z])
                                    r = np.random.rand()
                                    if r<PSUN:
                                        type_change(cj,EMPTY,PSUN,'evaporate')
                                        N_zhengfa+=1 
									
break
        printt(f'Surface evaporation {N_zhengfa} cells')
    def chongshua(self):
        # Scouring
        N_chongshua = 0
        for zi in np.arange(z0+h_tai+1):
            for xi in np.arange(x0-l_wave/2,x0+l_wave/2+1):
                # rdot = (H_total-zi+z0)*R_di/H_total
                y_delta = self.G.get_y_range(xi=xi,zi=zi)
                for yi in np.arange(y0-y_delta,y0+y_delta+1):
                    xi,yi,zi = int(xi),int(yi),int(zi)
                    # print([xi,yi,zi])
                    if self.G.is_inside(np.array([xi,yi,zi])) or self.G.is_on(np.array([xi,yi,zi])):
                        cj = self.get_cell((xi,yi,zi))
                        # print((xi,yi,zi))
                        assert cj is not False
                        if cj is not False:
                            if cj.type != EMPTY:
                                
                                # if z <=H_base and check_on_yuantai(P_0,R_di,h_tai,R_up,P):
                                # if cj.type == EMPTY:
                                # if np.random.rand()<WATER_EMPTY_FILL:
                                # type_change(cj,WATER,WATER_EMPTY_FILL,'flush')
                                if cj.type == SAND:
                                    # Washable objects
                                    x,y,z = cj.loc
                                    P = np.array([x,y,z])
                                    Ti = self.get_unstable_degree(cj,rule='sand')
                                    # if Ti >= T2 and np.random.rand() <Ti/(26*b):
                                    if Ti >= T2 and np.random.rand() <(Ti+26*c)/(T_sacle):
                                        type_change(cj,WATER,(Ti+26*c)/(T_sacle),'scouring')
                                        N_chongshua+=1
                                break
        # if print_True:
        printt(f'Wash out the sand cells: (N_chongshua)pcs')