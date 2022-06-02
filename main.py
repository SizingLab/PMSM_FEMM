from motor import PM_motor

from femm_wrapper.femm_mag_wrapper import MagneticFEMMWrapper
from femm_wrapper.femm_thermal_wrapper import ThermalFEMMWrapper

# Parameters
rotor_type = 'Halbach'          # 'IPM'/'SPM'/'Halabch' 
stator_type = 'concentrated'    # 'concetrated'
motif = '10/12'                 # Number of magent/number of slot  --> '10/12' or '14/12' pr '16/18' 
repetition = 2                  # if =1 all motor, if =2 half motor, if =3 thrid motor etc, exemple: 10/12 with reptition of 2 = 20/24, with reptition of 3 = 30/36
                            

motor = PM_motor(MagneticFEMMWrapper, rotor_type, stator_type, motif, repetition)


"""if __name__ == '__main__':
    Motor1 = Motor(r = 0.7, R = 3.5, h = 1 / 0.01, nb_wire = 4)
    wire_base = WireModel()
    
    thermal_wrapper = ThermalFEMMWrapper()
    mag_wrapper = MagneticFEMMWrapper()
    
    thermal_model = ThermalGeomGeneration(wire1, thermal_wrapper)
    execute_model(thermal_model)
    
    mag_model = MagGeomGeneration(wire1, mag_wrapper)
    execute_model(mag_model, freq = 50)"""
    motor.draw()
#    motor.compute()
#    motor.print()
