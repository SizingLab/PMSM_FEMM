from Project.motor import PM_motor
from femm_wrapper.femm_mag_wrapper import MagneticFEMMWrapper
from femm_wrapper.femm_thermal_wrapper import ThermalFEMMWrapper

# Parameters
rotor_type = 'Halbach'          # 'IPM'/'SPM'/'Halbach'
stator_type = 'concentrated'    # 'concentrated'
motif = '10/12'                 # Number of magnet/number of slot  --> '10/12' or '14/12' pr '16/18'
repetition = 2                  # if =1 all motor, if =2 half motor, if =3 thrid motor etc, exemple: 10/12 with reptition of 2 = 20/24, with reptition of 3 = 30/36
rotor_geomgeneration = True

motor = PM_motor(ThermalFEMMWrapper(), rotor_type, rotor_geomgeneration, stator_type, motif, repetition)


if __name__ == '__main__':

    motor.draw()
    motor.compute()
    motor.print()
