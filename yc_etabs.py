#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

PROGRAM      : YC_ETABS
DESPRIPITION : 定義 ETABS 物件 及 函數

AUTHOR       : YUCHEN LIN
CREATE DATE  : 2020.12.02
VERSION      : v1.2
UPDATE       :
    1. Modify output e2k filenames

"""    

import os

class etabs9p5 :
    def __init__(self, filename = None) :
        if filename == None :
            ls = os.listdir()
            
            for i in range(len(ls)) :
                if 'e2k' in ls[i] :
                    filename = ls[i].split('.')[0]
        
        self.filename = filename
        
        self.e2k = open(filename + '.e2k', 'r',encoding = 'Big5').readlines()
        
    def read_e2k(self, keyword = 'PROGRAM INFORMATION') :
        e2k = self.e2k
        
        for i in range(len(e2k)) :
            if keyword in e2k[i] :
                start_idx = i+1
                break
        
        for j in range(i+1,len(e2k)) :
            if '$' == e2k[j][0] :
                end_idx = j-1
                break
        
        if e2k[end_idx] == '\n' :
            end_idx -= 1
        
        txt = e2k[start_idx:(end_idx+1)]
        
        return (txt, (start_idx, end_idx))
    
    def get_story_data(self) :
        return self.read_e2k('STORIES - IN SEQUENCE FROM TOP')
    
    def get_material(self) :
        return self.read_e2k('MATERIAL PROPERTIES')
    
    def get_frame_section(self) :
        return self.read_e2k('FRAME SECTIONS')
    
    def get_rc_section(self) :
        return self.read_e2k('CONCRETE SECTIONS')
    
    def get_plate_property(self) :
        return self.read_e2k('WALL/SLAB/DECK PROPERTIES')
    
    def get_line_connectivity(self) :
        return self.read_e2k('LINE CONNECTIVITIES')
    
    def get_line_assign(self) :
        return self.read_e2k('LINE ASSIGNS')
    
    def get_rc_design_overwrite(self) :
        return self.read_e2k('CONCRETE DESIGN OVERWRITES')
    
    def get_rc_design_prefer(self):
        return self.read_e2k('CONCRETE DESIGN PREFERENCES')
    
    def get_units(self) :
        t =  self.read_e2k('CONTROLS')
        temp = t[0][0].split()
        
        funit = temp[1].split('"')[1]
        lunit = temp[2].split('"')[1]
        
        return funit, lunit
    
    def output_e2k(self, prefix = '', suffix = '_new') :
        e2k = self.e2k
        
        with open(prefix + self.filename + suffix + '.e2k', 'w', \
                  encoding = 'Big5') as f :
            for s in e2k :
                f.write(s)
        
#### MAIN ####
a = etabs9p5()      
        
        
        
        
        
        
        
        