from motor import PM_motor_mag
from motor import PM_motor_thermal
from femm_wrapper.femm_mag_wrapper import MagneticFEMMWrapper
from femm_wrapper.femm_thermal_wrapper import ThermalFEMMWrapper

# Parameters
rotor_type = 'Halbach'          # 'IPM'/'SPM'/'Halabch' 
stator_type = 'concentrated'    # 'concetrated'
motif = '10/12'                 # Number of magent/number of slot  --> '10/12' or '14/12' pr '16/18' 
repetition = 2                  # if =1 all motor, if =2 half motor, if =3 thrid motor etc, exemple: 10/12 with reptition of 2 = 20/24, with reptition of 3 = 30/36
                            

motor = PM_motor_mag(rotor_type, stator_type, motif, repetition)


if __name__ == '__main__':
    motor.draw()
#    motor.compute()
#    motor.print()
