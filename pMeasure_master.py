# Author: Alex Cui
# Email: alexxucui@gmail.com
# James Hone Group, Columbia University

import visa
import math
import time
import matplotlib.pyplot as plt
#import numpy as np
from matplotlib.pyplot import savefig
import csv

GPIB_keithley_1 = 23
GPIB_keithley_2 = 24
GPIB_lakeshore  = 12
GPIB_lockin_1 = 7
GPIB_lockin_2 = 8
GPIB_lockin_3 = 9
#GPIB_address_3 = 25 topgate


#Open Instrument

rm = visa.ResourceManager()

#Keithley

backgate = rm.open_resource('GPIB0::%d::INSTR' % GPIB_keithley_1)
backgate.write(':outp on')

source = rm.open_resource('GPIB0::%d::INSTR' % GPIB_keithley_2)
source.write(':outp on')

#Lock-in

lockin_1 = rm.open_resource('GPIB0::%d::INSTR' % GPIB_lockin_1)    #v_2p
lockin_2 = rm.open_resource('GPIB0::%d::INSTR' % GPIB_lockin_2)    #v_4p
lockin_3 = rm.open_resource('GPIB0::%d::INSTR' % GPIB_lockin_3)    #I_sd

#Temperature controller

lakeshore = rm.open_resource('GPIB0::%d::INSTR' % GPIB_lakeshore)

#Sweep function

def read_temp():
    A_temp = lakeshore.ask('KRDG? A')     # A is the sample temperature
    B_temp = lakeshore.ask('KRDG? B')
    print "A:", str(A_temp).split('+')[1]
    print "B:", str(B_temp).split('+')[1]

def goto_temp(target = 100):
    if target >= 30:
       lakeshore.write('ramp 1,1,10')
       lakeshore.write('ramp 2,1,10')
       lakeshore.write('setp 1,' + str(target-1))
       lakeshore.write('setp 2,' + str(target-10))
       lakeshore.write('range 1,3')
       lakeshore.write('range 2,3')
    if target  <= 20 & target > 10:
       lakeshore.write('ramp 1,1,1')
       lakeshore.write('ramp 2,1,1')
       lakeshore.write('setp 1,' + str(target))
       lakeshore.write('setp 2,' + str(target-3))
       lakeshore.write('range 1,0')
       lakeshore.write('range 2,0')
    if target  <= 10:
       lakeshore.write('range 1,0')
       lakeshore.write('range 2,0')

#clear the data
def clear_data():

    global Ig_list
    Ig_list = list()
    global Vg_list
    Vg_list = list()

    global Isd_list
    Isd_list = list()
    global Vsd_list
    Vsd_list = list()
    global Rsd_list
    Rsd_list = list()

    global T_list
    T_list = list()

    global X1_list
    X1_list = list()
    global Y1_list
    Y1_list = list()
    global R1_list
    R1_list = list()
    global theta1_list
    theta1_list = list()

    global X2_list
    X2_list = list()
    global Y2_list
    Y2_list = list()
    global R2_list
    R2_list = list()
    global theta2_list
    theta2_list = list()

    global X3_list
    X3_list = list()
    global Y3_list
    Y3_list = list()
    global R3_list
    R3_list = list()
    global theta3_list
    theta3_list = list()

    global R2p_list
    R2p_list = list()
    global R4p_list
    R4p_list = list()
    global Rc_list
    Rc_list = list()


def bg_sweep(start=0.0, end=3.0, step=100, delay=100):

    Range = 1.1*(math.fabs(end) if math.fabs(end) > math.fabs(start) else math.fabs(start))
    backgate.write(':SOUR:VOLT:RANG ' + str(Range))
    backgate.write(':SOUR:DEL '+ str(delay/1000))
    stage = (end - start)/step

    for i in range(step+1):
        Vg = start + stage*i
        backgate.write(':source:volt %s' % Vg)

def sd_sweep(start=0.0, end=3.0, step=100, delay=100):

    Range = 1.1*(math.fabs(end) if math.fabs(end) > math.fabs(start) else math.fabs(start))
    source.write(':SOUR:VOLT:RANG ' + str(Range))
    source.write(':SOUR:DEL ' + str(delay/1000))
    stage = (end - start)/step

    for i in range(step+1):
        Vs = start + stage*i
        source.write(':source:volt %s' % Vs)

#Transfer curve

def transfer(vsd=0.01, vb_low=0, vb_high=80, step=100, delay=0, pair='0.5um'):

    vsd = float(vsd)
    vb_low = float(vb_low)
    vb_high = float(vb_high)

#    temp_A = lakeshore.ask('KRDG? A')
#    T = float(temp_A.split('+')[1])

    filename = time.strftime("%Y%m%d", time.localtime()) +'-'+'transfer'+'-'+'pair'+pair +'-'+'vsd'+'-'+str(vsd*1000)+'mV' \
               +'-'+'vbg'+'-'+str(vb_low)+'-'+str(vb_high)+'V'+'-'+'20K'

    if filename[-4:] != '.csv':
       filename += '.csv'

    sd_sweep(start=0.0, end=vsd, step=1000, delay=100)
    bg_sweep(start=0.0, end=vb_low, step=4000, delay=100)

    Range = 1.1*(math.fabs(vb_high) if math.fabs(vb_high) > math.fabs(vb_low) else math.fabs(vb_low))
    backgate.write(':SOUR:VOLT:RANG ' + str(Range))
    backgate.write(':SOUR:DEL ' + str(delay/1000))
    stage = (vb_high - vb_low)/step

    clear_data()

    #real-time plotting
    plt.ion()

    for i in range(step+1):
        Vg = vb_low + stage*i
        backgate.write(':source:volt %s' % Vg)

        #  backgate.write('read?')
    	  #data = inst.read(':CURR')

        data_bg = backgate.read("TRACE:DATA")
        data_sd = source.read("TRACE:DATA")
       # temp_A = lakeshore.ask('KRDG? A')

        Ig = float(data_bg.split(',')[1]) * 1E9
        Vg = float(Vg)
        Is = float(data_sd.split(',')[1])
        Vs = float(vsd)
        Rs = Vs / Is
#       T = float(temp_A.split('+')[1])

        Vg_list.append(Vg)
        Ig_list.append(Ig)
        Vsd_list.append(Vs)
        Isd_list.append(Is)
        Rsd_list.append(Rs)
        #T_list.append(T)


        plt.subplot(2, 2, 1)
        plt.plot(Vg, Is, 'b.')
        plt.xlabel('Vbg (V)')
        plt.ylabel('Isd (A)')
        plt.grid(True)

        plt.subplot(2, 2, 2)
        if Is > 0:
           plt.semilogy(Vg, Is, 'b.')
           plt.xlabel('Vbg (V)')
           plt.ylabel('Isd (A)')
           plt.grid(True)

        plt.subplot(2, 2, 3)
        if Rs >0:
           plt.semilogy(Vg, Rs, 'b.')
           plt.xlabel('Vbg (V)')
           plt.ylabel('Rsd (Ohm)')
           plt.grid(True)

        plt.subplot(2, 2, 4)
        plt.plot(Vg, Ig, 'r.')
        plt.xlabel('Vbg (V)')
        plt.ylabel('Ig (nA)')
        plt.grid(True)

        plt.tight_layout()
        plt.pause(0.0001)

    plt.ioff()
    savefig(filename[:-4]+'.png')

    csv_out = open(filename, 'wb')
    mywriter = csv.writer(csv_out)
    mywriter.writerow(( 'Vg', 'Ig(nA)', 'Vsd','Isd','Rsd') )

    for row in zip(Vg_list,Ig_list,Vsd_list,Isd_list,Rsd_list):
        mywriter.writerow(row)

    csv_out.close()

    bg_sweep(start = vb_high, end=0.0, step=4000, delay=100)
    sd_sweep(start=vsd, end=0.0, step=1000, delay=100)


#ourput curve

def output(vsd=0.1, vb_low=0.0, vb_high=80.0, v_step=4, step=100, delay=100, pair = '0.5um'):

    vsd = float(vsd)
    vb_low = float(vb_low)
    vb_high = float(vb_high)

#    temp_A = lakeshore.ask('KRDG? A')
#    T =float(temp_A.split('+')[1])

    sd_sweep(start=0.0, end=-vsd, step=1000, delay=100)
    bg_sweep(start=0.0, end=vb_low, step=4000, delay=100)

    Range = 1.1*(math.fabs(vsd))
    source.write(':SOUR:VOLT:RANG ' + str(Range))
    source.write(':SOUR:DEL ' + str(delay/1000))
    stage = 2 * vsd / step
    v_stage = (vb_high - vb_low) / v_step

    #real-time plotting
    plt.ion()

    for j in range(v_step+1):

        clear_data()

        filename = time.strftime("%Y%m%d", time.localtime()) +'-'+'output'+'-'+'pair'+pair+'-'+'vsd'+'-'+str(vsd*1000)+'mV' \
                   +'-'+'vbg'+'-'+ str(vb_low+j*v_stage)+ 'V' + '-'  + '20K'

        if filename[-4:] != '.csv':
           filename += '.csv'

        #plt.figure(vb_low + j * v_stage)

        for i in range(step+1):

            Vs = -vsd + stage*i
            source.write(':source:volt %s' % Vs)
            #source.write('read?')

            data_bg = backgate.read("TRACE:DATA")
            data_sd = source.read("TRACE:DATA")
            # temp_A = lakeshore.ask('KRDG? A')

            Ig = float(data_bg.split(',')[1]) *1E9
            Vg = float(vb_low + j * v_stage)
            Is = float(data_sd.split(',')[1])
            Vs = float(Vs)
            Rs = math.fabs(Vs / Is)
            # T = float(temp_A.split('+')[1])

            Vg_list.append(Vg)
            Ig_list.append(Ig)
            Vsd_list.append(Vs)
            Isd_list.append(Is)
            Rsd_list.append(Rs)
            #T_list.append(T)

            plt.subplot(2, 2, 1)
            plt.plot(Vs, Is, 'b.')
            plt.xlabel('Vsd (V)')
            plt.ylabel('Isd (A)')
            plt.grid(True)

            plt.subplot(2, 2, 2)
            if Is > 0:
               plt.semilogy(Vs, Is, 'b.')
               plt.xlabel('Vsd (V)')
               plt.ylabel('Isd (A)')
               plt.grid(True)

            plt.subplot(2, 2, 3)
            plt.plot(Vs, Rs, 'b.')
            plt.xlabel('Vsd (V)')
            plt.ylabel('Rsd (Ohm)')
            plt.grid(True)

            plt.subplot(2, 2, 4)
            plt.plot(Vs, Ig, 'r.')
            plt.xlabel('Vsd (V)')
            plt.ylabel('Ig (nA)')
            plt.grid(True)

            plt.tight_layout()
            plt.pause(0.0001)


            savefig(filename[:-4]+'.png')
            plt.ioff()


            csv_out = open(filename, 'wb')
            mywriter = csv.writer(csv_out)
            mywriter.writerow(('Vg', 'Ig(nA)', 'Vsd','Isd','Rsd'))

            for row in zip(Vg_list,Ig_list,Vsd_list,Isd_list,Rsd_list):
			 mywriter.writerow(row)

            csv_out.close()


        if j != v_step:
		bg_sweep(start = vb_low + j * v_stage , end= vb_low + (j+1) * v_stage, step = 4000, delay = 100)
		sd_sweep(start = vsd, end = -vsd, step = 1000, delay = 100)

    bg_sweep(start = vb_high, end= 0.0, step = 4000, delay = 100)
    sd_sweep(start = vsd, end = 0.0, step = 1000, delay = 100)

#Keithley go to zero state

def keithley(target_bg = 0, target_sd = 0):
    data_bg = backgate.read("TRACE:DATA")
    data_sd = source.read("TRACE:DATA")
    vbg = float(data_bg.split(',')[0])
    vsd = float(data_sd.split(',')[0])
    bg_sweep(start = float(vbg), end = float(target_bg), step = 4000, delay = 100)
    sd_sweep(start = float(vsd), end = float(target_sd), step = 1000, delay = 100)



def gate_leak_temp(vbg=80.0):

    bg_sweep(start = 0.0, end = float(vbg), step = 1000, delay = 100)
    sd_sweep(start = 0.0, end = float(vbg), step = 1000, delay = 100)

    filename = time.strftime("%Y%m%d", time.localtime()) +'-'+'Gateleak12_vs_T'+'vbg'+'-'+str(vbg)+'V'
    if filename[-4:] != '.csv':
			filename += '.csv'

    clear_data()

    plt.ion()

    while True:

          data_bg = backgate.read("TRACE:DATA")
          data_sd = source.read("TRACE:DATA")
          temp_A = lakeshore.ask('KRDG? A')

          Ig = float(data_bg.split(',')[1])
          Is = float(data_sd.split(',')[1])
          T = float(temp_A.split('+')[1])

          data_bg = backgate.read("TRACE:DATA")
          data_sd = source.read("TRACE:DATA")

          Ig_list.append(Ig)
          Isd_list.append(Is)
          T_list.append(T)


          plt.subplot(2, 1, 1)
          plt.plot(T_list, Ig_list, r'b-D')
          plt.xlabel('T (K)')
          plt.ylabel('Ig1 (A)')
          plt.grid(True)

          plt.subplot(2, 1, 2)
          plt.plot(T_list, Isd_list, r'b-D')
          plt.xlabel('T (K)')
          plt.ylabel('Ig2 (A)')
          plt.grid(True)

          plt.tight_layout()
          plt.pause(0.0001)

          csv_out = open(filename, 'wb')
          mywriter = csv.writer(csv_out)
          mywriter = csv.writer(csv_out)
          mywriter.writerow(('T', 'Ig1', 'Ig2'))

          for row in zip(T_list,Ig_list,Isd_list):
              mywriter.writerow(row)

          csv_out.close()

          time.sleep(10)


def lockin_probe(vb_low=0.0, vb_high=80.0, step=100, delay=100):

    vb_low = float(vb_low)
    vb_high = float(vb_high)

    filename = time.strftime("%Y%m%d", time.localtime()) +'-'+'lockin-transfer'+'-'+'sd-vxx'+'-'+'vbg'+'-'+str(vb_low)+'-'+str(vb_high)+'V'+'-'+'100K'

    if filename[-4:] != '.csv':
       filename += '.csv'

    bg_sweep(start=0.0, end=vb_low, step=1000, delay=100)

    Range = 1.1*(math.fabs(vb_high) if math.fabs(vb_high) > math.fabs(vb_low) else math.fabs(vb_low))
    backgate.write(':SOUR:VOLT:RANG ' + str(Range))
    backgate.write(':SOUR:DEL ' + str(delay/1000))
    stage = (vb_high - vb_low)/step

    clear_data()

    	#real-time plotting
    plt.ion()

    for i in range(step+1):
        Vg = vb_low + stage*i
        backgate.write(':source:volt %s' % Vg)

        # backgate.write('read?')
    	  # data = inst.read(':CURR')

        data_bg = backgate.read("TRACE:DATA")
        temp_A = lakeshore.ask('KRDG? A')

        T = float(temp_A.split('+')[1])

        Ig = float(data_bg.split(',')[1])
        Vg = round(Vg, 3)

        X1 = math.fabs(float(lockin_1.ask('OUTP? 1')))
        X1 = math.fabs(float(lockin_1.ask('OUTP? 1')))
        Y1 = float(lockin_1.ask('OUTP? 2'))
        Y1 = float(lockin_1.ask('OUTP? 2'))
        R1 = float(lockin_1.ask('OUTP? 3'))
        R1 = float(lockin_1.ask('OUTP? 3'))
        theta1 = float(lockin_1.ask('OUTP? 4'))
        theta1 = float(lockin_1.ask('OUTP? 4'))

        X2 = math.fabs(float(lockin_2.ask('OUTP? 1')))
        X2 = math.fabs(float(lockin_2.ask('OUTP? 1')))
        Y2 = float(lockin_2.ask('OUTP? 2'))
        Y2 = float(lockin_2.ask('OUTP? 2'))
        R2 = float(lockin_2.ask('OUTP? 3'))
        R2 = float(lockin_2.ask('OUTP? 3'))
        theta2 = float(lockin_1.ask('OUTP? 4'))
        theta2 = float(lockin_1.ask('OUTP? 4'))

        X3 = math.fabs(float(lockin_3.ask('OUTP? 1')))
        X3 = math.fabs(float(lockin_3.ask('OUTP? 1')))
        Y3 = float(lockin_3.ask('OUTP? 2'))
        Y3 = float(lockin_3.ask('OUTP? 2'))
        R3 = float(lockin_3.ask('OUTP? 3'))
        R3 = float(lockin_3.ask('OUTP? 3'))
        theta3 = float(lockin_3.ask('OUTP? 4'))
        theta3 = float(lockin_3.ask('OUTP? 4'))


        R_2p = math.fabs(X1 / X3)
        R_4p = math.fabs(X2 / X3)
        Rc = (R_2p - R_4p * 1 / 1)/2           # ohm


        T_list.append(T)


        Vg_list.append(Vg)
        Ig_list.append(Ig)

        X1_list.append(X1)
        Y1_list.append(Y1)
        R1_list.append(R1)
        theta1_list.append(theta1)

        X2_list.append(X2)
        Y2_list.append(Y2)
        R2_list.append(R2)
        theta2_list.append(theta2)

        X3_list.append(X3)
        Y3_list.append(Y3)
        R3_list.append(R3)
        theta3_list.append(theta3)


        R2p_list.append(R_2p)
        R4p_list.append(R_4p)
        Rc_list.append(Rc)


        plt.subplot(2, 5, 1)
        plt.plot(Vg_list, X1_list, r'b-D')
        plt.xlabel('Vbg (V)')
        plt.ylabel('V2p (V)')
        plt.grid(True)

        plt.subplot(2, 5, 3)
        plt.plot(Vg_list, X3_list, r'b-D')
        plt.xlabel('Vbg (V)')
        plt.ylabel('Isd (A)')
        plt.grid(True)

        plt.subplot(2, 5, 2)
        if R_2p > 0:
           plt.semilogy(Vg_list, R2p_list, r'b-D')
           plt.xlabel('Vbg (V)')
           plt.ylabel('R2p (Ohm)')
           plt.grid(True)

        plt.subplot(2, 5, 4)
        plt.plot(Vg_list, theta1_list, r'b-D')
        plt.xlabel('Vbg (V)')
        plt.ylabel('Theta_2p (degree)')
        plt.grid(True)

        plt.subplot(2, 5, 5)
        plt.plot(Vg_list, Ig_list, r'b-D')
        plt.xlabel('Vbg (V)')
        plt.ylabel('Ig (A)')
        plt.grid(True)

        ###################################

        plt.subplot(2, 5, 6)
        plt.plot(Vg_list, X2_list, r'b-D')
        plt.xlabel('Vbg (V)')
        plt.ylabel('V4p (V)')
        plt.grid(True)

        plt.subplot(2, 5, 8)
        if Rc > 0:
           plt.semilogy(Vg_list, Rc_list, r'b-D')
           plt.xlabel('Vbg (V)')
           plt.ylabel('Rc (ohm)')
           plt.grid(True)

        plt.subplot(2, 5, 7)
        if R_4p > 0:
           plt.semilogy(Vg_list, R4p_list, r'b-D')
           plt.xlabel('Vbg (V)')
           plt.ylabel('R4p (Ohm)')
           plt.grid(True)

        plt.subplot(2, 5, 9)
        plt.plot(Vg_list, theta2_list, r'b-D')
        plt.xlabel('Vbg (V)')
        plt.ylabel('Theta_4p (degree)')
        plt.grid(True)

        plt.subplot(2, 5, 10)
        plt.plot(Vg_list, T_list, r'b-D')
        plt.xlabel('Vbg (V)')
        plt.ylabel('T (K)')
        plt.grid(True)

        plt.tight_layout()

        plt.pause(0.0001)

        if i == step:
           savefig(filename[:-4]+'.png')
           plt.ioff()
                #plt.close()

    csv_out = open(filename, 'wb')
    mywriter = csv.writer(csv_out)
    mywriter.writerow(( 'Vg', 'V_2p', 'theta_2p','V_4p','theta_4p','R_2p','R_4p','Rc','Isd','Ig','T') )

    for row in zip(Vg_list,X1_list,Y1_list,X2_list,Y2_list,R2p_list,R4p_list,Rc_list,X3_list,Ig_list,T_list):
        mywriter.writerow(row)

    csv_out.close()

    bg_sweep(start = vb_high, end=0.0, step=1000, delay=100)















