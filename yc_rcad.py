#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

PROGRAM      : YC_RCAD
DESPRIPITION : 定義 RCAD 物件 及 函數

AUTHOR       : YUCHEN LIN
CREATE DATE  : 2020.11.25
UPDATE DATE  : 2021.05.14
VERSION      : v1.3
UPDATE       :
    1. Modify the method for reading beam size

"""    

# Create RCAD object
class rcad :
    def __init__(self, version = None) :
        self.version = version
        
# Create RCAD_BEAM object
class rbeam2016(rcad) :
    #####
    def __init__(self, rbeam_filename = 'tmp-Beam-Rebar.txt', version = 'RCAD2016') :
        super().__init__(version = version)
        
        self.rbeam_filename = rbeam_filename
        try :
            self.rbeam_datas = self.read_beam_data()
        except :
            print('No ' + self.rbeam_filename + ' to read !')
        
        self.rbeam_blocks = self.extract_beam_rebar()
        
        self.rbeam_db = self.read_blocks()

    #####    
    def read_beam_data(self) :
        with open(self.rbeam_filename, 'r') as f :
            return f.readlines()

    #####    
    def extract_beam_rebar(self) :
        block_list = []
        s = self.rbeam_datas
        
        for i in range(len(s)) :
            if i == 0 :
                temp = []
                temp.append(s[i])
            elif i == len(s) :
                block_list.append(temp)
            elif 'F.NO' in s[i] :
                block_list.append(temp)
                
                temp = []
                temp.append(s[i])
            else :
                temp.append(s[i])
        
        return block_list

    #####    
    def read_blocks(self) :
        blocks = self.rbeam_blocks
        
        db = []
        
        for i in range(len(blocks)) :
            block = blocks[i]
            
            db.append({
                'count' : self.count_beam(block), # int
                'beam_name' : self.find_beam_name(block), # list[str]
                'section' : self.find_section(block), # list[(b,h)]
                'rebar' : self.find_rebar(block), # dict{POS : (#,[(left,mid,right)])}
                'web' : self.find_web(block), # list[(#, num)]
                'stirrup' : self.find_stirrup(block) # list[((#L,numL),(#M,numM,(#R,numR)))]
                })
        
        return db
     
    #####
    def count_beam(self, block) :
        s = block[0].split()
        
        count = 0
        
        for i in range(len(s)) :
            if '"' in s[i] :
                count += 1
        
        return count
    
    #####
    def find_beam_name(self,block) :
        s = block[0].split()
        
        name = []
        
        for i in range(len(s)) :
            if '"' in s[i] :
                name.append(s[i].split('"')[1])
        
        return name
    
    #####
    def find_section(self,block) :
        s = block[0].split()
        ss = block[0].split('"')
        
        d = []
        
        # for i in range(len(s)) :
            # if '*' in s[i] :
            #     b = float(s[i][-len(s[i]):-1])
            #     h = float(s[i+1][-len(s[i+1]):-1])
                
            #     d.append([b,h])
            
        num = (len(ss)-1)/2
        
        for i in range(int(num)) :
            temp = ss[2 + i*2].split('(')[1].split(')')[0].split('*')
            
            d.append([float(temp[0]),float(temp[1])])
        
        return d
    
    #####
    def find_rebar(self,block) :
        rebar = {}
        
        for i in range(len(block)) :
            if 'TOP' in block[i] :
                break
        
        # TOP1 ZONE
        temp = block[i].split()
        del temp[0]
        
        rebar_size = temp[0]
        del temp[0]
        
        rebar_nums = []
        for j in range(0,len(temp),3) :
            rebar_nums.append([int(temp[j]), int(temp[j+1]),int(temp[j+2])])
            
        rebar['TOP1'] = [rebar_size, rebar_nums]
        
        i += 1
        
        # TOP2 ZONE
        temp = block[i].split()
        del temp[0]
        
        rebar_size = temp[0]
        del temp[0]
        
        rebar_nums = []
        for j in range(0,len(temp),3) :
            rebar_nums.append([int(temp[j]), int(temp[j+1]),int(temp[j+2])])
            
        rebar['TOP2'] = [rebar_size, rebar_nums]
        
        i += 2
        
        # BOT2 ZONE
        temp = block[i].split()
        del temp[0]
        
        rebar_size = temp[0]
        del temp[0]
        
        rebar_nums = []
        for j in range(0,len(temp),3) :
            rebar_nums.append([int(temp[j]), int(temp[j+1]),int(temp[j+2])])
            
        rebar['BOT2'] = [rebar_size, rebar_nums]
        
        i += 1
        
        # BOT1 ZONE
        temp = block[i].split()
        del temp[0]
        
        rebar_size = temp[0]
        del temp[0]
        
        rebar_nums = []
        for j in range(0,len(temp),3) :
            rebar_nums.append([int(temp[j]), int(temp[j+1]),int(temp[j+2])])
            
        rebar['BOT1'] = [rebar_size, rebar_nums]
        
        
        return rebar

    #####    
    def find_web(self,block) :
        for i in range(len(block)) :
            if 'WEB' in block[i] :
                s = block[i].split()
                break
        
        d = []
        
        for i in range(1,len(s)) :
            temp = s[i].split('#')
            
            d.append(['#'+temp[1], int(temp[0])])
        
        return d
            

    #####    
    def find_stirrup(self,block) :
        for i in range(len(block)) :
            if 'STIR' in block[i] :
                break

        temp = block[i].split()
        del temp[0]
        
        rebar_nums = []
        for j in range(0,len(temp),3) :
            rebar_num = []
            
            temp2 = temp[j:j+3]
            
            for k in range(len(temp2)) :
                rebar_num.append(\
                    [temp2[k].split('@')[0],\
                     float(temp2[k].split('@')[1])])
            
            rebar_nums.append(rebar_num)
        
        return rebar_nums
    
    ####
    def update_rbeam(self) :
        db = self.rbeam_db
        block = self.rbeam_blocks
        
        for j in range(len(block)) :
            jblock = block[j]
            
            for i in range(len(db)) :
                idb = db[i]
                
                if idb['beam_name'][0] in jblock[0].split('"') :
                    count = idb['count']
                    break
            
            # Modify rebar data
            top1 = jblock[1].split()
            top2 = jblock[2].split()
            bot2 = jblock[4].split()
            bot1 = jblock[5].split()
            
            k = 2
            for kk in range(count) :
                for kkk in range(3) :
                    top1[k] = str(idb['rebar']['TOP1'][1][kk][kkk])
                    top2[k] = str(idb['rebar']['TOP2'][1][kk][kkk])
                    bot2[k] = str(idb['rebar']['BOT2'][1][kk][kkk])
                    bot1[k] = str(idb['rebar']['BOT1'][1][kk][kkk])
                    
                    k += 1
            
            block[j][1] = ' '.join(top1)
            block[j][2] = ' '.join(top2)
            block[j][4] = ' '.join(bot2)
            block[j][5] = ' '.join(bot1)
        
            # Modify stirrup
            stir = jblock[7].split()
            
            k = 1
            for kk in range(count) :
                for kkk in range(3) :
                    temp = idb['stirrup'][kk][kkk]
                    temp[1] = str(int(temp[1]))
                    stir[k] = '@'.join(temp)
                    
                    k += 1
            
            block[j][7] = ' '.join(stir)
            
            # Modify web
            web = jblock[8].split()
            
            k = 1
            for kk in range(count) :
                temp = idb['web'][kk]
                temp = str(temp[1]) + temp[0]
                
                web[k] = temp
                
                k += 1
            
            block[j][8] = ' '.join(web)
            
        self.rbeam_blocks = block
    
    ####
    def output_rbeam(self, filename = None) :
        self.update_rbeam()
        
        block = self.blocks
        
        if filename == None :
            filename = 'new_' + self.rbeam_filename
        
        with open(filename, 'w') as f :
            for i in range(len(block)) :
                for j in range(len(block[0])) :
                    temp = block[i][j]
                    
                    if temp[-1] == '\n' :
                        f.write(block[i][j])
                    else :
                        f.write(block[i][j]+'\n')
    
    ####
    # def rbeam2sercb_rebar(self) :
        
        
    #     pass
        
    
# Create RCAD_COL object
class rcol2016(rcad) :
    #####
    def __init__(self, rcol_filename = 'tmp-Col-Rebar.txt', version = 'RCAD2016') :
        super().__init__(version = version)
        
        self.rcol_filename = rcol_filename
        try :
            self.rcol_datas = self.read_col_data()
        except :
            print('No ' + self.rcol_filename + ' to read !')
        
        self.rcol_blocks = self.extract_col_rebar()
        
        self.rcol_db = self.read_blocks()

    #####    
    def read_col_data(self) :
        with open(self.rcol_filename, 'r') as f :
            return f.readlines()

    #####    
    def extract_col_rebar(self) :
        block_list = []
        s = self.rcol_datas
        
        isStart = False
        
        for i in range(len(s)) :
            if (not isStart) and ('RCAD_ASCO COLUMN-LINE' in s[i]) :
                isStart = True
                
                temp = []
                # temp.append(s[i])
                
            elif i == len(s)-1 :
                temp.append(s[i])
                block_list.append(temp)
                
            elif (isStart) and ('RCAD_ASCO COLUMN-LINE' in s[i]) :
                block_list.append(temp)
                
                temp = []
                # temp.append(s[i])
                
            elif isStart :
                temp.append(s[i])
        
        return block_list

    #####    
    def read_blocks(self) :
        blocks = self.rcol_blocks
        
        db = []
        
        for i in range(len(blocks)) :
            block = blocks[i]
            
            for j in range(int(block[1])) :
                jblock  = block[j*5+2:j*5+7]
                
                db.append({
                    'col_name' : self.find_col_name(jblock,block[0]), # str
                    'section' : self.find_section(jblock), # (b,h)
                    'rebar' : self.find_rebar(jblock), # ((numx,numy),rebararray)
                    'tie' : self.find_tie(jblock), # (#, (numx,numy)
                    'stirrup' : self.find_stirrup(jblock), # list[((#D,numD),(#M,numM,(#U,numU)))]
                    'As' : self.find_As(jblock),
                    'story' : self.find_story(jblock),
                    'sect_name' : block[0]
                    })
        
        return db
    
    #####
    def find_story(self,block) :
        s = block[0].split()
        
        return s[0]
    
    #####
    def find_col_name(self,block,col_name) :
        s = block[0].split()
        
        col_name = col_name.split('"')[1]
        
        return s[0]+col_name
    
    #####
    def find_section(self,block) :
        s = block[1].split()
        
        b = int(float(s[0]))
        h = int(float(s[1]))
                
        return (b,h)
    
    #####
    def find_rebar(self,block) :
        x_rebar_data = block[2].split()
        y_rebar_data = block[3].split()
        
        num_x_rebar = int(x_rebar_data[0])
        num_y_rebar = int(y_rebar_data[0])
        
        x_rebar = x_rebar_data[2:]
        y_rebar = y_rebar_data[2:]
        
        rebar = [(num_x_rebar, num_y_rebar), (x_rebar, y_rebar)]
        
        return rebar

    #####    
    def find_tie(self,block) :
        x_rebar_data = block[2].split()
        y_rebar_data = block[3].split()
        
        num_x_tie = int(x_rebar_data[1])
        num_y_tie = int(y_rebar_data[1])
        
        return (num_x_tie, num_y_tie)     

    #####    
    def find_stirrup(self,block) :
        stirrup_data = block[4].split()
        
        stir = []
        nums = []
        
        for i in range(3) :
            stirNO = stirrup_data[i].split('@')[0]
            spacing = int(stirrup_data[i].split('@')[1].split(',')[0])
            
            if i == 1 :
                num = stirrup_data[i].split('@')[1].split(',')[1]
            else :
                num = ''
            
            stir.append((stirNO, spacing))
            nums.append(num)
        
        stir.append(nums)
        
        return stir
    
    #####
    def find_As(self, block) :
        return float(block[1].split()[2])
    
    ####
    def update_rcol(self) :
        db = self.rcol_db
        block = self.rcol_blocks
        
        for j in range(len(block)) :
            jblock = block[j]
            
            num_story = int(jblock[1])
            
            for jj in range(num_story) :
                jjblock = jblock[jj*5+2: jj*5+7]
                
                for idb in db :
                    if (idb['sect_name'] in jblock[0]) and \
                        (idb['story'] in jjblock[0].split()[0]) :
                            break
                
                # Modify main rebar
                rebars = idb['rebar']
                tie = idb['tie']
                
                for k in range(2) :
                    num_rebar = rebars[0][k]
                    num_tie = tie[k]
                    rebar = rebars[1][k]
                    
                    block[j][jj*5+4+k] = \
                        '  ' + str(num_rebar) + '  ' + str(num_tie) +\
                        '  ' + '  '.join(rebar) + '\n'
                
                # Modify stirrup
                stirrup = idb['stirrup']
                s = '  '
                for k in range(3) :
                    temp = stirrup[k]
                    
                    s += temp[0] + '@' + str(temp[1])
                    
                    if k == 1 :
                        s += ',%d' % int(stirrup[3][1])
                    
                    s += '   '
                    
                s += '\n'
                block[j][jj*5+6] = s
                
            
        self.rcol_blocks = block
    
    ####
    def output_rcol(self, filename = None) :
        
        self.update_rcol()
        
        block = self.rcol_blocks
        datas = self.rcol_datas
        
        if filename == None :
            filename = 'new_' + self.rcol_filename
        
        for iblock in block :
            for j in range(len(datas)) :
                if '$RCAD_ASCO COLUMN-LINE' in datas[j] :
                    if iblock[0] in datas[j+1] :
                        for i in range(len(iblock)) :
                            datas[(j+1+i)] = iblock[i]
        
        self.rcol_datas = datas
        
        with open(filename, 'w') as f :
            for temp in datas :
                f.write(temp)

rcol=rcol2016()
rbeam = rbeam2016()



