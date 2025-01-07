#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

PROGRAM      : SERCB SECTION PREPROCESS
DESPRIPITION : SERCB斷面檔前置處理

AUTHOR       : YUCHEN LIN
CREATE DATE  : 2020.12.06
UPDATE DATE  : 2021.11.30
VERSION      : v1.0.2
UPDATE       :
    1. Ignoring those beam and column name which cannot be find
"""
print('00. 讀取模組...')

import time

start_time = time.process_time()

import yc_etabs as et
import yc_rcad as rd
from rc_info import *
from tkinter import messagebox

print('    完成讀取模組！')

def mat_fix_M0(etabs) :
    mat, idx = etabs.get_material()
    
    for i in range(len(mat)) :
        imat = mat[i]
        
        if 'M 0' in imat :
            mat[i] = imat.replace('M 0', 'M 1.0E-15')
    
    etabs.e2k[idx[0]:idx[1]+1] = mat
    
    return etabs

def extract_beamnum2linelabel(filename = 'Beam-Log.txt'):
    txt = open(filename, 'r', encoding = 'Big5').readlines()
    
    idx = txt.index('相關梁群組已經更新,細項如下:\n')+3
    
    beam_list = []
    
    for i in range(idx, len(txt)) :
        if '***' in txt[i] :
            break
        elif '\n' == txt[i] :
            continue
        
        beam = txt[i].split()
        
        if beam[1] == 'none' :
            continue
        else :
            beam_list.append(beam)
    
    return beam_list

def extract_colnum2linelabel(filename = 'Column-Log.txt'):
    txt = open(filename, 'r', encoding = 'Big5').readlines()
    
    idx = txt.index('相關柱群組已經更新,細項如下:\n')+3
    
    col_list = []
    
    for i in range(idx, len(txt)) :
        if '***' in txt[i] :
            break
        elif '\n' == txt[i] :
            continue
        
        col = txt[i].split()
        
        if col[1] == 'none' :
            continue
        else :
            col_list.append(col)
    
    return col_list

def e2k_beam_modify(etabs) :
    # matetial = []
    frame = []
    concrete = []
    
    # mat = etabs.get_material()[0]
    frm = etabs.get_frame_section()[0]
    rcs = etabs.get_rc_section()[0]
    lin = etabs.get_line_assign()[0]
    
    beamNO = extract_beamnum2linelabel()
    
    for i in beamNO :
        story = i[0]
        beam = i[1]
        label = i[2:]
        
        for j in range(len(lin)) :
            line = lin[j].split()
            
            if 'SECTION' in line :
                story1 = line[2].split('"')[1]
                label1 = line[1].split('"')[1]
                
                if (story == story1) and (label1 in label) :
                    sectname_old = line[line.index('SECTION')+1]
                    sectname_new = '"%s%s"' % (story,beam)
                    
                    lin[j] = lin[j].replace(sectname_old, sectname_new)
                    
                    for sect in rcs :
                        if sectname_old in sect :
                            concrete.append(sect.replace(sectname_old,sectname_new))
                            break
                    for sect in frm :
                        if sectname_old in sect :
                            frame.append(sect.replace(sectname_old,sectname_new))
                            break
                
                else :
                    continue
            else :
                continue
    
    return frame, concrete, lin

def e2k_col_modify(etabs, direction = 'X') :
    # matetial = []
    frame = []
    concrete = []
    
    # mat = etabs.get_material()[0]
    frm = etabs.get_frame_section()[0]
    rcs = etabs.get_rc_section()[0]
    lin = etabs.get_line_assign()[0]
    
    colNO = extract_colnum2linelabel()
    
    story_data = etabs.get_story_data()[0]
    stories = []
    for temp in story_data :
        stories.append(temp.split()[1].split('"')[1])
    
    for i in colNO :
        story = i[0]
        col = i[1]
        label = i[2:]
        
        for j in range(len(lin)) :
            line = lin[j].split()
            
            if 'SECTION' in line :
                story1 = line[2].split('"')[1]
                label1 = line[1].split('"')[1]
                
                if (story == story1) and (label1 in label) :
                    sectname_old = line[line.index('SECTION')+1]
                    sectname_new = '"%s%s"' % (stories[stories.index(story)+1],col)
                    
                    lin[j] = lin[j].replace(sectname_old, sectname_new)
                    
                    for sect in rcs :
                        if sectname_old in sect :
                            concrete.append(sect.replace(sectname_old,sectname_new))
                            break
                    for sect in frm :
                        if sectname_old in sect :
                            if direction == 'Y' :
                                temp = sect.split()
                                D = temp[temp.index('D')+1]
                                B = temp[temp.index('B')+1]
                                
                                temp[temp.index('D')+1] = B
                                temp[temp.index('B')+1] = D
                                
                                sect = ' '.join(temp) + '\n'
                                
                                ####
                                
                                temp = lin[j].split()
                                
                                temp[temp.index('ANG')+1] = '90'
                                
                                lin[j] = ' '.join(temp) + '\n'
                                
                            frame.append(sect.replace(sectname_old,sectname_new))
                            break
                
                else :
                    continue
            else :
                continue
    
    return frame, concrete, lin

def e2k_revise_frame_data(frame, concrete, lin, etabs) :
    e2k = etabs.e2k
    
    # Line Assignment
    lin_idx = etabs.get_line_assign()[1]
    del e2k[lin_idx[0] : lin_idx[1]]
    for i in range(len(lin)) :
        e2k.insert(lin_idx[0], lin[i])
        
    # Concrete Section
    rcs_idx = etabs.get_rc_section()[1]
    for i in range(len(concrete)) :
        e2k.insert(rcs_idx[0], concrete[i])
    
    # Frame Section
    frm_idx = etabs.get_frame_section()[1]
    for i in range(len(frame)) :
        e2k.insert(frm_idx[0], frame[i])
        
    return e2k
    
def sercb_beam_sect(etabs, rbeam, frm, conc) :
    sect_def = []
    rebar_loc = []
    mander_met = []
    
    funit, lunit = etabs.get_units()
    db = rbeam.rbeam_db
    
    if lunit == 'M' :
        lfactor = 100
    elif lunit == 'CM' :
        lfactor = 1
    else :
        lfactor = 0
        
    if funit == 'TON' :
        ffactor = 1000
    elif funit == 'KGF' :
        ffactor = 1
    else :
        ffactor = 0
    
    used_sect = []
    
    for i in range(len(frm)) :
        ifrm = frm[i].split()
        
        sect = ifrm[ifrm.index('FRAMESECTION')+1].split('"')[1]
        mat = ifrm[ifrm.index('MATERIAL')+1].split('"')[1]
        height = float(ifrm[ifrm.index('D')+1])
        width = float(ifrm[ifrm.index('B')+1])
        
        if sect in used_sect :
            continue
        else :
            used_sect.append(sect)
            
        for j in range(len(conc)) :
            if not sect in conc[j] :
                continue
            else :
                jconc = conc[j].split()
                
                # cover = float(jconc[jconc.index('COVERTOP')+1])
                
                
                break
        
        haveRebar = True
        for j in range(len(db)) :
            jdb = db[j]
            beam_names = jdb['beam_name']
            beam_story = jdb['beam_story'][0]

            beam_story_names = [beam_story + beam_name for beam_name in beam_names]
            
            if not sect in beam_story_names :
                if j == len(db)-1 :
                    haveRebar = False
                continue
            else :
                idx = beam_story_names.index(sect)
                
                rebar = jdb['rebar']
                stir = jdb['stirrup']
                web = jdb['web']
                
                rebar_size = rebar['TOP1'][0]
                stir_size = '#' + stir[idx][0][0].split('#')[-1]
                web_size = web[idx][0]
                
                top1 = rebar['TOP1'][1][idx]
                top2 = rebar['TOP2'][1][idx]
                bot1 = rebar['BOT1'][1][idx]
                bot2 = rebar['BOT2'][1][idx]
                
                stir_spacing = max(stir[idx][0][1], stir[idx][-1][1])
                stir_spacingM = stir[idx][1][1]
                                   
                web_num = web[idx][1]
                
                dbm, Abm = rebar_info(rebar=rebar_size)
                dbt, Abt = rebar_info(rebar=stir_size)
                
                rebar_type = 'SD420'
                
                cover = 4+dbm/2+dbt
                
                break
            
            
        
        if  not haveRebar : # Cannot Find rebar
            continue
        
        
        s = ['%s\t%s\t\t%.2f\t%.2f\t%.2f\t%s\t%.2f\t%.2f\t0\n' % \
             (sect, sect, width, height, 
              (cover-dbm/2-dbt), stir_size, stir_spacing, stir_spacingM)]
        
        top = [top1[0]+top2[0],99, top1[-1]+top2[-1]]
        bot = [bot1[0]+bot2[0],99, bot1[-1]+bot2[-1]]
        
        topidx = top.index(min(top))
        botidx = bot.index(min(bot))
            
        rebar_num = [top1[topidx], top2[topidx],
                     bot2[botidx], bot1[botidx]]
        
        s.append('%s%s%s\t%s%s*%d(%.2f,%.2f-%.2f,%.2f)\n' % \
                 (sect, ' '*11, rebar_type, ' '*10, rebar_size, rebar_num[0], 
                  cover, cover, width-cover, cover))
        if rebar_num[1] != 0 :
            s.append('%s%s%s\t%s%s*%d(%.2f,%.2f-%.2f,%.2f)\n' % \
                 (sect, ' '*11, rebar_type, ' '*10, rebar_size, rebar_num[1], 
                  cover, cover+2.5, width-cover, cover+2.5))
        if rebar_num[2] != 0 :
            s.append('%s%s%s\t%s%s*%d(%.2f,%.2f-%.2f,%.2f)\n' % \
                 (sect, ' '*11, rebar_type, ' '*10, rebar_size, rebar_num[2], 
                      cover, height-cover-2.5, width-cover, height-cover-2.5))
        s.append('%s%s%s\t%s%s*%d(%.2f,%.2f-%.2f,%.2f)\n' % \
                 (sect, ' '*11, rebar_type, ' '*10, rebar_size, rebar_num[3], 
                  cover, height-cover, width-cover, height-cover))
            
        sect_def.append(s[0])
        
        for j in range(1, len(s)) :    
            rebar_loc.append(s[j])
        
        #
        mat_list = etabs.get_material()[0]
        for temp in mat_list :
            temp2 = temp.split()
            
            if (mat in temp2[1]) and ('CONCRETE' in temp2[3]) :
                fc = float(temp2[7])
                fys = float(temp2[9])
                
                break
        
        temp = [stir[idx][0][0].split('#'), 
                stir[idx][1][0].split('#'), 
                stir[idx][2][0].split('#')]
        Av = []
        tie_num = []
        for xxx in temp:
            if xxx[0] == '' :
                num = 2
            else :
                num = 2*int(xxx[0])
            
            Av.append(num*rebar_info(rebar='#'+xxx[-1])[1])
            tie_num.append(num)
            
        Av_min = min(Av)
        tie = min(tie_num)
        
        mander_met.append(' %s\t%.2f\t\t%.2f\t%.2f\t%.2f\t%.2f\n' % 
                          (sect, fc, fys, Av_min, tie, 2))
        
    return sect_def, rebar_loc, mander_met

def sercb_col_sect(etabs, rcol, frm, conc, direction = 'X') :
    sect_def = []
    rebar_loc = []
    mander_met = []
    
    funit, lunit = etabs.get_units()
    db = rcol.rcol_db
    
    if lunit == 'M' :
        lfactor = 100
    elif lunit == 'CM' :
        lfactor = 1
    else :
        lfactor = 0
        
    if funit == 'TON' :
        ffactor = 1000
    elif funit == 'KGF' :
        ffactor = 1
    else :
        ffactor = 0
    
    used_sect = []
    
    # Run all frame sections
    for i in range(len(frm)) :
        ifrm = frm[i].split()
        
        sect = ifrm[ifrm.index('FRAMESECTION')+1].split('"')[1]
        mat = ifrm[ifrm.index('MATERIAL')+1].split('"')[1]
        height = float(ifrm[ifrm.index('D')+1])
        width = float(ifrm[ifrm.index('B')+1])
        
        # Check if this section is used
        if sect in used_sect :
            continue
        else :
            used_sect.append(sect)
        
        # Find the concrete section and fix it
        for j in range(len(conc)) :
            if not sect in conc[j] :
                continue
            else :
                jconc = conc[j].split()
                
                # cover = float(jconc[jconc.index('COVER')+1])
                
                break
        
        # Find rebar of this section
        haveRebar = True
        for j in range(len(db)) :
            jdb = db[j]
            col_name = jdb['col_name']
            
            if not sect in col_name :
                if j == len(db)-1 :
                    haveRebar = False
                continue
            else :
                
                rebar = jdb['rebar']
                stir = jdb['stirrup']
                # tie = jdb['tie']
                
                rebar_size = '#' + rebar[1][0][0].split('#')[-1]
                stir_size = stir[0][0]
                
                num_x_rebar, num_y_rebar = rebar[0]
                x_rebar, y_rebar = rebar[1]
                
                stir_spacing = stir[0][1]
                stir_spacingM = stir[1][1]
                
                dbm, Abm = rebar_info(rebar=rebar_size)
                dbt, Abt = rebar_info(rebar=stir_size)
                
                rebar_type = 'SD420'
                
                cover = 4+dbm/2+dbt
                
                tie = []
                for irebar in rebar[1] :
                    num_tie = 2
                    
                    for jrebar in irebar :
                        num_tie += int(jrebar.split('#')[0])
                    
                    tie.append(num_tie)
                
                break
        
        if  not haveRebar : # Cannot Find rebar
            continue
        
        s = ['%s\t%s\t\t%.2f\t%.2f\t%.2f\t%s\t%.2f\t%.2f\t0\n' % \
             (sect, sect, width, height, 
              (cover-dbm/2-dbt), stir_size, stir_spacing, stir_spacingM)]
        
        # Arrange the rebar position
        if direction == 'Y' :
            x_rebar, y_rebar = y_rebar, x_rebar
            num_x_rebar, num_y_rebar = num_y_rebar, num_x_rebar
        
        y_spacing = (height-2*cover) / (num_x_rebar-1) 
        
        for j in range(num_x_rebar) :
            x_coor = [cover, width-cover]
            y_coor = cover + j*y_spacing
            
            if j == 0 or j == (num_x_rebar-1) :
                count = 0
                for k in range(num_y_rebar) :
                    if len(y_rebar[k].split('#')) == 3 :
                        count += 1
                
                s.append('%s%s%s\t%s%s*%d(%.2f,%.2f-%.2f,%.2f)\n' % \
                 (sect, ' '*11, rebar_type, ' '*10, rebar_size, num_y_rebar+count, 
                  x_coor[0], y_coor, x_coor[1], y_coor))

            else :
                s.append('%s%s%s\t%s%s*%d(%.2f,%.2f-%.2f,%.2f)\n' % \
                 (sect, ' '*11, rebar_type, ' '*10, rebar_size, 2, 
                  x_coor[0], y_coor, x_coor[1], y_coor))
                    
                if len(x_rebar[j].split('#')) == 3 :
                    s.append('%s%s%s\t%s%s*%d(%.2f,%.2f-%.2f,%.2f)\n' % \
                     (sect, ' '*11, rebar_type, ' '*10, rebar_size, 2, 
                      x_coor[0]+rebar_info(rebar = rebar_size)[0], y_coor,\
                      x_coor[1]-rebar_info(rebar = rebar_size)[0], y_coor))
            
        sect_def.append(s[0])
        
        for j in range(1, len(s)) :    
            rebar_loc.append(s[j])
        
        # Material Data
        mat_list = etabs.get_material()[0]
        for temp in mat_list :
            temp2 = temp.split()
            
            if (mat in temp2[1]) and ('CONCRETE' in temp2[3]) :
                fc = float(temp2[7])
                fys = float(temp2[9])
                
                break
        
        if direction == 'X' :
            tie3, tie2 = tie
        elif direction == 'Y' :
            tie2, tie3 = tie
            
        Av = tie2 * Abt
        
        mander_met.append(' %s\t%.2f\t\t%.2f\t%.2f\t%.2f\t%.2f\n' % 
                          (sect, fc, fys, Av, tie2, tie3))
            
        
    return sect_def, rebar_loc, mander_met

def sect_output(bsect_def, csect_def, brebar_loc, crebar_loc, etabs, suffix = '_new') :
    filename = etabs.filename
    
    sect_def = bsect_def + csect_def
    rebar_loc = brebar_loc + crebar_loc
    
    with open(filename + suffix + '.SECT', 'w') as f:
        f.write('$Unit\n')
        f.write('KGF-CM\n')
        f.write('$ RC Rectangle Section Definitions\n')
        f.write('$ Name	RCMaterial	Width	Height	Cover	SNo	Spacing	SpacingM	Angle\n')
        f.write('$ 			(cm)	(cm)	(cm)		(cm)	(cm)\n')
        
        for temp in sect_def :
            f.write(temp)
        
        f.write('\n$ End RC Rectangle Section Definitions\n\n' + \
              '$ Steels Location\n' +\
              '$ Name		Material		No. X Y\n')
        
        for temp in rebar_loc :
            f.write(temp)
        
        f.write('\n$ End Steels Location\n\n$ Analysis Options\n'+\
                '$ Name  Options\n*	-echo=SectionAnalysis.txt -echo-mode=Append\n'+\
                '$ End Analysis Options\n')

def met_output(etabs, met, suffix = '_new') :
    filename = etabs.filename
    
    with open(filename + suffix + '.MET', 'w') as f:
        f.write('$Unit\n')
        f.write('KGF-CM\n\n')
        f.write('$ Kawashima constitutive law\n')
        f.write('$ Name	Fc		Fsy	Av	EL(2)	EL(3)\n')
        f.write('$ 	(kgf/cm^2)	(kgf/cm^2)		(cm^2)		(cm)	(cm)\n\n'+\
                '$ End Kawashima constitutive law\n\n')
        f.write('$ Mander constitutive law\n')
        f.write('$ Name	Fc		Fsy	Av	N2	N3\n')
        f.write('$ 	(kgf/cm^2)	(kgf/cm^2)		(cm^2)\n')
        
        for temp in met :
            f.write(temp)
        
        f.write('\n$ End Mander constitutive law\n\n' + \
              '$ Steel stress strain\n' +\
              '$ Name		YieldingStress		Es\n' +\
              '$ 		(kgf/cm^2)		(kgf/cm^2)\n')
        
        steel = [['SD280', 2800],
                 ['SD420', 4200],
                 ['SD490', 4900],
                 ['SD560', 5600]]
            
        for sname, fy in steel  :  
            f.write(' %s\t\t%.2f \t\t%.2f\n' % (sname, fy, 2040000))
        
        f.write('\nEnd steel stress strain')

##### MAIN #####
print('01. 讀取ETABS及RCAD檔...')

etx = et.etabs9p5()
ety = et.etabs9p5()

etx = mat_fix_M0(etx)
ety = mat_fix_M0(ety)
print('    01. ETABS讀取成功！(%s.e2k)' % etx.filename)

rbeam = rd.rbeam2019()
print('    02. RCAD梁配筋讀取成功！(tmp-Beam-Rebar.txt)')

rcol = rd.rcol2019()
print('    03. RCAD柱配筋讀取成功！(tmp-Col-Rebar.txt)')

print('02. 修改ETABS桿件名稱...')
bfrm, bconc, blin = e2k_beam_modify(etx)
etx.e2k = e2k_revise_frame_data(bfrm, bconc, blin, etx)
ety.e2k = e2k_revise_frame_data(bfrm, bconc, blin, ety)
print('    01. 梁斷面已修正！')

cfrmx, cconcx, clinx = e2k_col_modify(etx, direction = 'X')
etx.e2k = e2k_revise_frame_data(cfrmx, cconcx, clinx, etx)

cfrmy, cconcy, cliny = e2k_col_modify(ety, direction = 'Y')
ety.e2k = e2k_revise_frame_data(cfrmy, cconcy, cliny, ety)
print('    02. 柱斷面已修正')

etx.output_e2k(suffix='_X')
ety.output_e2k(suffix='_Y')
print('    03. 已輸出調整後ETABS檔！(%s_X.e2k & %s_Y.e2k)' % (etx.filename,ety.filename))

print('03. 輸出SERCB所需斷面配筋檔...(*.SECT,.*.MET)')
bsect_def, brebar_loc, mander_met = sercb_beam_sect(etx, rbeam, bfrm, bconc)
print('    01. 梁配筋處理完成！')

csectx_def, crebarx_loc, mander_met_x = sercb_col_sect(etx, rcol, cfrmx, cconcx, direction = 'X')
csecty_def, crebary_loc, mander_met_y = sercb_col_sect(ety, rcol, cfrmy, cconcy, direction = 'Y')
print('    02. 柱配筋處理完成！')

sect_output(bsect_def, csectx_def, brebar_loc, crebarx_loc, etx, suffix='_X')
sect_output(bsect_def, csecty_def, brebar_loc, crebary_loc, ety, suffix='_Y')
print('    03. SECT檔輸出完成！')

met_output(etx, mander_met+mander_met_x, suffix='_X')
met_output(etx, mander_met+mander_met_y, suffix='_Y')
print('    04. MET檔輸出完成！')

end_time = time.process_time()
messagebox.showinfo(message = ('--- ETABS斷面調整 & SECT & MET檔已輸出！ ---'+\
                                '\n(Spend %.3f sec)')% (end_time-start_time))
