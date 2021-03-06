# pMeasure
pMeasure is a python-written script that can control mutlipe national instruments for measurement.

## PyVisa
pMeasure required [PyVisa](https://pyvisa.readthedocs.io/en/stable/) to connect to instruments.
You can istall it using pip:

	$ pip install -U pyvisa

## Usage

_Transfer Curve_

    transfer(vsd=0.01, vb_low=0, vb_high=80, step=100, delay=0, pair='0.5um')

vsd: Source-drain bias  
vb_low: Gate bias low value  
vb_high: Gate bias high value  
step: number of gate bias steps  

_Output Curve_

	output(vsd=0.1, vb_low=0.0, vb_high=80.0, v_step=4, step=100, delay=0, pair = '0.5um')


If you want to return both Keithey to 0, use:

	keithley(target_bg = 0, target_sd = 0)


The data in csv formate and a screenshot of the plot will be saved in your root folder.


## Plotting


Example of of transfer cruve measurement of a n-type semiconductor device:

![Transfer Curve](https://github.com/alexxucui/pMeasure/blob/master/images/transfer_curve.png)

Isd: Source-drain current  
Rsd: Source-drain resistance  
Ig: Gate leak current  

Output curve measurement of a n-type semiconductor device:

![Output Curve](https://github.com/alexxucui/pMeasure/blob/master/images/output_curve.png)




