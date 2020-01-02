from utils.common.is800_2007 import IS800_2007
from utils.common.material import *
from utils.common.other_standards import *
from Common import *
import sqlite3
import math
import numpy as np
from utils.common.common_calculation import *

class Bolt(Material):

    def __init__(self, grade=None, diameter=None, bolt_type="", material_grade="", bolt_hole_type="",
                 edge_type="", mu_f=0.0, corrosive_influences=True):
        super(Bolt, self).__init__(material_grade)
        if grade is not None:
            self.bolt_grade = list(np.float_(grade))
        if diameter is not None:
            self.bolt_diameter = list(np.float_(diameter))
        self.bolt_type = bolt_type
        self.bolt_hole_type = bolt_hole_type
        self.edge_type = edge_type
        self.mu_f = float(mu_f)
        self.connecting_plates_tk = None

        self.bolt_grade_provided = 0.0
        self.bolt_diameter_provided = 0.0

        self.bolt_shank_area = 0.0
        self.bolt_net_area = 0.0

        self.bolt_shear_capacity = 0.0
        self.bolt_bearing_capacity = 0.0
        self.bolt_capacity = 0.0
        self.bolts_required = 0
        self.bolt_group_capacity = 0.0
        self.bolt_line = 0.0
        self.bolts_one_line = 0.0
        self.bolt_force = 0.0

        self.bolt_fu = 0.0
        self.bolt_fy = 0.0

        if corrosive_influences == "Yes":
            self.corrosive_influences = True
        else:
            self.corrosive_influences = False

        self.min_pitch = 0.0
        self.min_gauge = 0.0
        self.min_edge_dist = 0.0
        self.min_end_dist = 0.0
        self.max_spacing = 0.0
        self.max_edge_dist = 0.0
        self.max_end_dist = 0.0
        self.dia_hole = 0.0

    def __repr__(self):
        repr = "Bolt\n"
        repr += "Type: {}\n".format(self.bolt_type)
        repr += "Diameter: {}\n".format(self.bolt_diameter)
        repr += "Grade: {}\n".format(self.bolt_grade)
        repr += "Diameter Provided: {}\n".format(self.bolt_diameter_provided)
        repr += "Grade Provided: {}\n".format(self.bolt_grade_provided)

        repr += "Diameter of Hole: {}\n".format(self.dia_hole)
        repr += "Minimum Pitch: {}\n".format(self.min_pitch)
        repr += "Minimum Gauge: {}\n".format(self.min_gauge)
        repr += "Minimum Edge Distance: {}\n".format(self.min_edge_dist)
        repr += "Minimum End Distance: {}\n".format(self.min_end_dist)
        repr += "Maximum Edge Distance: {}\n".format(self.max_edge_dist)
        repr += "Maximum End Distance: {}\n".format(self.max_end_dist)
        repr += "Maximum Spacing: {}\n".format(self.max_spacing)


        repr += "Bolt Shear Capacity: {}\n".format(self.bolt_shear_capacity)
        repr += "Bolt Bearing Capacity: {}\n".format(self.bolt_bearing_capacity)
        repr += "Bolt Capacity: {}\n".format(self.bolt_capacity)
        return repr

    def calculate_bolt_capacity(self, bolt_diameter_provided, bolt_grade_provided, connecting_plates_tk, n_planes):
        """

        :param bolt_type: bearing or friction grip bolt
        :param bolt_grade: grade of bolt
        :param member_fu: ultimate strength of member
        :param plate_fu: ultimate strength of plate (This is taken same as member strength)
        :param bolt_hole_type: standard or over-sized
        :param bolt_dia: diameter of bolt
        :param n_planes: number of shear planes
        :param edge_type: shear or hand flame cut
        :param connecting_plates_tk: thickness of connecting plates
        :param mu_f: slip factor for friction grip bolts
        :param member_fy: yield strength of member
        :param plate_fy: yield strength of plate
        :param corrosive_influences: yes or no
        :return: capacity of bolt (shear and bearing), ultimate strength of bolt and yield strength of bolt
        """
        self.bolt_diameter_provided = bolt_diameter_provided
        self.bolt_grade_provided = bolt_grade_provided
        self.connecting_plates_tk = list(np.float_(connecting_plates_tk))

        [self.bolt_shank_area, self.bolt_net_area] = IS1367_Part3_2002.bolt_area(self.bolt_diameter_provided)
        [self.bolt_fu, self.bolt_fy] = IS1367_Part3_2002.get_bolt_fu_fy(self.bolt_grade_provided)

        if self.bolt_type == "Bearing Bolt":
            self.bolt_shear_capacity = IS800_2007.cl_10_3_3_bolt_shear_capacity(
                f_u=self.bolt_fu, A_nb=self.bolt_net_area, A_sb=self.bolt_shank_area, n_n=n_planes, n_s=0)
            self.bolt_bearing_capacity = IS800_2007.cl_10_3_4_bolt_bearing_capacity(
                f_u=self.fu, f_ub=self.bolt_fu, t=min(self.connecting_plates_tk), d=self.bolt_diameter_provided,
                e=self.min_edge_dist, p=self.min_pitch, bolt_hole_type=self.bolt_hole_type)
            self.bolt_capacity = min(self.bolt_shear_capacity, self.bolt_bearing_capacity)

        elif self.bolt_type == "Friction Grip Bolt":
            self.bolt_shear_capacity = IS800_2007.cl_10_4_3_bolt_slip_resistance(
                f_ub=self.bolt_fu, A_nb=self.bolt_net_area, n_e=n_planes, mu_f=self.mu_f, bolt_hole_type=self.bolt_hole_type)
            self.bolt_bearing_capacity = 'N/A'
            self.bolt_capacity = self.bolt_shear_capacity

        return self.bolt_capacity, self.bolt_fu, self.bolt_fy
        pass

    def calculate_bolt_spacing_limits(self, bolt_diameter_provided,connecting_plates_tk,bolt_hole_type):
        self.bolt_hole_type=bolt_hole_type
        self.connecting_plates_tk = list(np.float_(connecting_plates_tk))
        self.bolt_diameter_provided = bolt_diameter_provided
        self.min_pitch = IS800_2007.cl_10_2_2_min_spacing(self.bolt_diameter_provided)
        self.min_gauge = IS800_2007.cl_10_2_2_min_spacing(self.bolt_diameter_provided)
        self.min_edge_dist = IS800_2007.cl_10_2_4_2_min_edge_end_dist(self.bolt_diameter_provided, self.bolt_hole_type,
                                                                      self.edge_type)
        self.min_end_dist = self.min_edge_dist
        self.max_spacing = IS800_2007.cl_10_2_3_1_max_spacing(self.connecting_plates_tk)
        self.max_edge_dist = IS800_2007.cl_10_2_4_3_max_edge_dist(self.connecting_plates_tk, self.fy,
                                                                  self.corrosive_influences)
        self.max_end_dist = self.max_edge_dist
        self.dia_hole = IS800_2007.cl_10_2_1_bolt_hole_size(self.bolt_diameter_provided, self.bolt_hole_type)


class Nut(Material):

    def __init__(self, diameter=0.0, material_grade=""):
        self.diameter = diameter
        super(Nut, self).__init__(material_grade)

    def __repr__(self):
        repr = "Nut\n"
        repr += "Diameter: {}\n".format(self.diameter)
        return repr


class Section(Material):

    def __init__(self, designation, material_grade=""):
        super(Section, self).__init__(material_grade)
        self.designation = designation
        self.mass = 0.0
        self.area = 0.0
        self.depth = 0.0
        self.flange_width = 0.0
        self.web_thickness = 0.0
        self.flange_thickness = 0.0
        self.flange_slope = 0.0
        self.root_radius = 0.0
        self.toe_radius = 0.0
        self.mom_inertia_z = 0.0
        self.mom_inertia_y = 0.0
        self.rad_of_gy_z = 0.0
        self.rad_of_gy_y = 0.0
        self.elast_sec_mod_z = 0.0
        self.elast_sec_mod_y = 0.0
        self.plast_sec_mod_z = 0.0
        self.plast_sec_mod_y = 0.0
        self.source = 0.0

    def connect_to_database_update_other_attributes(self, table, designation):
        conn = sqlite3.connect(PATH_TO_DATABASE)
        db_query = "SELECT * FROM " + table + " WHERE Designation = ?"
        cur = conn.cursor()
        cur.execute(db_query, (designation,))
        row = cur.fetchone()
        self.mass = row[2]
        self.area = row[3]
        self.depth = row[4]
        self.flange_width = row[5]
        self.web_thickness = row[6]
        self.flange_thickness = row[7]
        #TODO:FIX DATA BASE INDICES
        # self.flange_slope = row[18]
        # self.root_radius = row[8]
        self.flange_slope = row[9]
        self.root_radius = row[9]
        self.toe_radius = row[9]
        self.mom_inertia_z = row[10]
        self.mom_inertia_y = row[11]
        self.rad_of_gy_z = row[12]
        self.rad_of_gy_y = row[13]
        self.elast_sec_mod_z = row[14]
        self.elast_sec_mod_y = row[15]
        self.plast_sec_mod_z = row[16]
        self.plast_sec_mod_y = row[17]
        self.source = row[19]

        conn.close()

    def __repr__(self):
        repr = "Section\n"
        repr += "Designation: {}\n".format(self.designation)
        repr += "fy: {}\n".format(self.fy)
        repr += "fu: {}\n".format(self.fu)
        return repr

class Beam(Section):

    def __init__(self, designation, material_grade):
        super(Beam, self).__init__(designation, material_grade)
        self.connect_to_database_update_other_attributes("Beams", designation)

    def min_plate_length(self):
        return 0.6 * self.depth

    def max_plate_length(self):

        clear_depth = self.depth - 2*self.flange_thickness - 2*self.root_radius
        return clear_depth

class Column(Section):

    def __init__(self, designation, material_grade):
        super(Column, self).__init__(designation, material_grade)
        self.connect_to_database_update_other_attributes("Columns", designation)


class Weld(Material):

    def __init__(self, size=0.0, length=0.0, material_grade=""):
        self.size = size
        self.length = length
        super(Weld, self).__init__(material_grade)

    def __repr__(self):
        repr = "Weld\n"
        repr += "Size: {}\n".format(self.size)
        repr += "Length: {}\n".format(self.length)
        return repr


class Plate(Bolt):

    def __init__(self, thickness=0.0, length=0.0, width=0.0, gap=0.0, material_grade=""):
        super(Plate, self).__init__(material_grade=material_grade)
        self.thickness = thickness
        self.length = length
        self.width = width
        self.gap = float(gap)
        self.moment_demand = 0.0
        self.pitch_provided = 0.0
        self.gauge_provided = 0.0
        self.edge_dist_provided = 0.0
        self.end_dist_provided = 0.0

    def get_web_plate_l_req(self, bolts_one_line, pitch, end_dist):
        web_plate_l_req = float((bolts_one_line - 1) * pitch + 2 * end_dist)
        return web_plate_l_req

    def get_spacing_adjusted(self, gauge_pitch, edge_end):
        while gauge_pitch > self.max_spacing:
            edge_end += 5
            gauge_pitch -= 5
        return gauge_pitch, edge_end

    def get_web_plate_l_bolts_one_line(self, web_plate_l_max, web_plate_l_min, bolts_required,bolt_dia,connecting_plates_tk,bolt_hole_type):
        super(Plate, self).calculate_bolt_spacing_limits(bolt_dia,connecting_plates_tk,bolt_hole_type)
        max_bolts_one_line = int(((web_plate_l_max - (2 * self.min_end_dist)) / self.min_pitch) + 1)
        bolt_line = int(math.ceil((float(bolts_required) / float(max_bolts_one_line))))
        bolts_one_line = max(int(math.ceil(float(bolts_required) / float(bolt_line))), 2)
        web_plate_l = max(web_plate_l_min, self.get_web_plate_l_req (bolts_one_line, self.min_pitch, self.min_end_dist))

        return bolt_line, bolts_one_line, web_plate_l

    def get_pitch_end_dist(self, web_plate_l, bolts_one_line):
        """

        :param web_plate_l: length of plate
        :param min_end_dist: minimum end distance
        :param bolts_one_line: bolts in one line
        :param max_spacing: maximum pitch
        :param max_end_dist: maximum end distance
        :return: pitch, end distance, length of plate (false if applicable)
        """
        pitch = round_up((web_plate_l - (2 * self.min_end_dist)) / (bolts_one_line - 1), multiplier=1)
        end_dist = (web_plate_l - pitch * (bolts_one_line - 1)) / 2
        if pitch > self.max_spacing:
            pitch, end_dist = self.get_spacing_adjusted(pitch, end_dist)
            if end_dist >= self.max_end_dist:
                web_plate_l = False
        return pitch, end_dist, web_plate_l

    def get_vres(self, bolts_one_line, pitch, gauge, bolt_line, shear_load, ecc):
        """

        :param bolts_one_line: number of bolts in one line
        :param pitch: pitch
        :param gauge: gauge
        :param bolt_line: number of bolt lines
        :param shear_load: shear load
        :param ecc: eccentricity
        :return: resultant load on bolt due to eccentricity of shear force
        """
        length_avail = (bolts_one_line - 1) * pitch
        ymax = length_avail / 2
        xmax = gauge * (bolt_line - 1) / 2
        r_sq = 0
        n = float(bolts_one_line) / 2.0 - 0.5
        b = float((bolt_line - 1)) / 2
        for x in np.arange(b, -b - 1, -1):
            for y in np.arange(-n, n + 1, 1):
                r_sq = r_sq + ((gauge * x) ** 2 + (abs(y) * pitch) ** 2)
        sigma_r_sq = r_sq
        vbv = shear_load / (bolts_one_line * bolt_line)
        moment_demand = round(shear_load * ecc, 3)
        tmh = moment_demand * ymax / sigma_r_sq
        tmv = moment_demand * xmax / sigma_r_sq
        vres = math.sqrt((vbv + tmv) ** 2 + tmh ** 2)
        return vres

    def get_bolt_red(self, bolts_one_line, pitch, bolt_capacity, bolt_dia):
        """

        :param bolts_one_line: bolts in one line
        :param pitch: pitch
        :param bolt_capacity: capacity of bolt
        :param bolt_dia: diameter of bolt
        :return: reduced bolt capacity if long joint condition is met
        """
        length_avail = (bolts_one_line - 1) * pitch
        if length_avail > 15 * bolt_dia:
            beta_lj = 1.075 - length_avail / (200 * bolt_dia)
            bolt_capacity_red = beta_lj * bolt_capacity
        else:
            bolt_capacity_red = bolt_capacity
        return bolt_capacity_red

    def get_web_plate_details(self, bolt_dia, web_plate_l_min, web_plate_l_max, bolt_capacity, bolt_line_limit, shear_load, gap,
                              shear_ecc,connecting_plates_tk,bolt_hole_type):
        """

        :param bolt_dia: diameter of bolt
        :param bolt_hole_type: holt type (standard or oversize)
        :param edge_type: shear flame or hand flame cut
        :param connecting_plates_tk: thickness of all connecting plates
        :param member_fy: yield strength of member
        :param plate_fy: yield strength of plate
        :param corrosive_influences
        :param web_plate_l_input: input value of plate length
        :param web_plate_l_min: minimum plate length
        :param web_plate_l_max: maximum plate length
        :param bolt_capacity: capacity of bolt
        :param bolt_line_limit: maximum number of bolt lines allowed
        :param shear_load: load along the length
        :param gap: gap between members which adds up to eccentricity
        :param shear_ecc: if eccentricity effect needs to be considered this value should be passed as "True"
        :return: web_plate_l, bolt_line, bolts_one_line, bolts_required, bolt_capacity_red, vres, moment_demand, \
               pitch, gauge, edge_dist, end_dist, a.min_edge_dist, a.min_pitch, a.max_spacing, a.max_edge_dist
        """

        # initialising values to start the loop
        bolts_required = max(int(math.ceil(shear_load / bolt_capacity)), 3)
        # calculation of  bolts in one line and check for given web plate height = 0 or user input value
        [bolt_line, bolts_one_line, web_plate_l] = self.get_web_plate_l_bolts_one_line(web_plate_l_max, web_plate_l_min,
                                                                                    bolts_required,bolt_dia,connecting_plates_tk,bolt_hole_type)
        bolts_required = bolt_line * bolts_one_line
        vres = bolt_capacity + 1
        bolt_capacity_red = bolt_capacity
        moment_demand = 0

        while bolt_line <= bolt_line_limit and vres > bolt_capacity:
            # for calculated length and bolts in one line, pitch,end dist and updated value of plate is calculated
            [pitch, end_dist, web_plate_l] = self.get_pitch_end_dist(web_plate_l, bolts_one_line)
            # Horizontal Shear due to eccentricity of load
            gauge = self.min_gauge
            edge_dist = self.min_edge_dist
            # If length is not false and check for shear eccentricity is true resultant force in bolt is calculated
            if shear_ecc is True:
                ecc = (gauge * max((bolt_line-1.5),0)) + edge_dist + gap
                moment_demand = shear_load * ecc
                while True:
                    vres = self.get_vres(bolts_one_line, pitch,
                                      gauge, bolt_line, shear_load, ecc)
                    bolt_capacity_red = self.get_bolt_red(bolts_one_line,
                                                       pitch, bolt_capacity,
                                                       bolt_dia)
                    # if input is 0, length of plate is increased for calculated bolts in one line.
                    # This increases spacing which decreases resultant force
                    if vres > bolt_capacity_red:
                        if web_plate_l + 10 <= web_plate_l_max:
                            web_plate_l += 10
                            [pitch, end_dist, web_plate_l] = self.get_pitch_end_dist(web_plate_l, bolts_one_line)
                        # If length cannot be increased number of bolts is increased by 1 and loop is repeated
                        else:
                            bolts_required += 1
                            # calculation of  bolts in one line and check for given web plate height = 0
                            # or user input value
                            [bolt_line, bolts_one_line, web_plate_l] = self.get_web_plate_l_bolts_one_line\
                                (web_plate_l_max, web_plate_l_min, bolts_required,bolt_dia,connecting_plates_tk)
                            break
                    else:
                        break
            else:
                break
        self.width = gap + edge_dist * 2 + gauge * (bolt_line - 1)
        self.length = web_plate_l
        self.bolt_line = bolt_line
        self.bolts_one_line = bolts_one_line
        self.bolts_required = bolt_line * bolts_one_line
        self.bolt_capacity = bolt_capacity_red
        self.bolt_force= vres
        self.moment_demand = moment_demand
        self.pitch_provided = pitch
        self.gauge_provided = gauge
        self.edge_dist_provided = edge_dist
        self.end_dist_provided = end_dist

    def __repr__(self):
        repr = "Plate\n"
        repr += "Thickness: {}\n".format(self.thickness)
        repr += "Length: {}\n".format(self.length)
        repr += "Width: {}\n".format(self.width)
        repr += "Bolt Lines: {}\n".format(self.bolt_line)
        repr += "Bolts in One Line: {}\n".format(self.bolts_one_line)
        repr += "Bolts Required: {}\n".format(self.bolts_required)
        repr += "Bolt Capacity Reduced: {}\n".format(self.bolt_capacity)
        repr += "Bolt Force: {}\n".format(self.bolt_force)
        repr += "Moment Demand: {}\n".format(self.moment_demand)
        repr += "Pitch Provided: {}\n".format(self.pitch_provided)
        repr += "Gauge Provided: {}\n".format(self.gauge_provided)
        repr += "Edge Distance Provided: {}\n".format(self.edge_dist_provided)
        repr += "End Distance Provided: {}\n".format(self.end_dist_provided)
        return repr


class Angle(Material):

    def __init__(self, designation, material_grade):
        super(Angle, self).__init__(material_grade)
        self.designation = designation

        self.leg_a_length = 0.0
        self.leg_b_length = 0.0
        self.thickness = 0.0

        self.connect_to_database_update_other_attributes(designation)

        self.length = 0.0

    def __repr__(self):
        repr = "Angle\n"
        repr += "Designation: {}\n".format(self.designation)
        return repr

    def connect_to_database_update_other_attributes(self, designation):
        conn = sqlite3.connect(PATH_TO_DATABASE)
        db_query = "SELECT AXB, t FROM Angles WHERE Designation = ?"
        cur = conn.cursor()
        cur.execute(db_query, (designation,))
        row = cur.fetchone()

        axb = row[0]
        axb = axb.lower()
        self.leg_a_length = float(axb.split("x")[0])
        self.leg_b_length = float(axb.split("x")[1])
        self.thickness = row[1]

        conn.close()

class I_sectional_Properties(object):

    def calc_Mass(self,D,B,t_w,t_f,alpha=90,r_1=0,r_2=0):
        self.A = ((2 * B * t_f) + ((D - 2 * t_f) * t_w)) / 100
        self.M = 7850 * self.A / 10000
        return round(self.M,1)

    def calc_Area(self,D,B,t_w,t_f,alpha=90,r_1=0,r_2=0):
        self.A = ((2*B*t_f) + ((D-2*t_f)*t_w))/100
        return round(self.A,1)

    def calc_MomentOfAreaZ(self,D,B,t_w,t_f,alpha=90,r_1=0,r_2=0):
        self.I_zz = ((D - 2*t_f)**3 * t_w /12 + (B*t_f**3)/6+(B/2*t_f*(D-t_f)**2))/10000
        return round(self.I_zz,1)

    def calc_MomentOfAreaY(self,D,B,t_w,t_f,alpha=90,r_1=0,r_2=0):
        self.I_yy = ((D-2*t_f)*t_w**3 /12 + B**3*t_f/6)/10000
        return round(self.I_yy,1)

    def calc_RogZ(self,D,B,t_w,t_f,alpha=90,r_1=0,r_2=0):
        self.A = ((2*B*t_f) + ((D-2*t_f)*t_w))/100
        self.I_zz = ((D - 2*t_f)**3 * t_w /12 + (B*t_f**3)/6+(B/2*t_f*(D-t_f)**2))/10000
        self.r_z = math.sqrt(self.I_zz / self.A)
        return round(self.r_z,2)

    def calc_RogY(self,D,B,t_w,t_f,alpha=90,r_1=0,r_2=0):
        self.A = ((2*B*t_f) + ((D-2*t_f)*t_w))/100
        self.I_yy = ((D-2*t_f)*t_w**3 /12 + B**3*t_f/6)/10000
        self.r_y = math.sqrt(self.I_yy / self.A)
        return round(self.r_y,2)

    def calc_ElasticModulusZz(self,D,B,t_w,t_f,alpha=90,r_1=0,r_2=0):
        self.I_zz = ((D - 2*t_f)**3 * t_w /12 + (B*t_f**3)/6+(B/2*t_f*(D-t_f)**2))/10000
        self.Z_ez = (self.I_zz * 2*10) / (D)
        return round(self.Z_ez,1)

    def calc_ElasticModulusZy(self,D,B,t_w,t_f,alpha=90,r_1=0,r_2=0):
        self.I_yy = ((D-2*t_f)*t_w**3 /12 + B**3*t_f/6)/10000
        self.Z_ey = (self.I_yy * 2*10) / (B)
        return round(self.Z_ey,1)

    def calc_PlasticModulusZpz(self,D,B,t_w,t_f,alpha=90,r_1=0,r_2=0):
        self.A = ((2*B*t_f) + ((D-2*t_f)*t_w))/100
        self.y_p = (((D - 2*t_f)**2*t_w/8 + B*t_f*(D-t_f)/2) / ((D-t_f)/2*t_w + B*t_f ))/10
        self.Z_pz =(2 * (self.A / 2 * self.y_p))
        return round(self.Z_pz,1)

    def calc_PlasticModulusZpy(self,D,B,t_w,t_f,alpha=90,r_1=0,r_2=0):
        self.A = ((2*B*t_f) + ((D-2*t_f)*t_w))/100
        self.z_p = ((((D-2*t_f)*t_w**2)/8 + (B*t_f*B)/4)/((D-2*t_f)*t_w/2 + (B*t_f)))
        self.Z_py = 2 * (self.A / 2 * self.z_p)
        return round(self.Z_py,1)