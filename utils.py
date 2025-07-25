import os
import time
import math

from pymol import cmd
from rdkit import Chem
from rdkit.Chem import AllChem
from MolKit_mock import Read, PdbWriter
from openbabel import openbabel
from urllib.error import HTTPError
from urllib.request import urlopen
from plip.basic import config
from plip.structure.preparation import PDBComplex
from plip.visualization.pymol import PyMOLVisualizer

__all__ = ['AttrDict', 'draw_gridbox', 'convert_dimension_to_coordinates',
	'convert_coordinates_to_dimension', 'get_atom_types_from_pdbqt',
	'get_molecule_center_from_pdbqt', 'time_format', 'convert_pdbqt_to_pdb',
	'ligand_efficiency_assessment', 'get_molecule_information', 'convert_ki_to_log',
	'time_elapse', 'generate_complex_pdb', 'get_complex_interactions',
	'interaction_visualize', 'get_dimension_from_pdb', 'load_molecule_from_file',
	'convert_string_to_pdb', 'memory_format', 'get_molecule_residues', 'sdf_file_parser',
	'get_sdf_props', 'get_residue_bonds', 'convert_pdbqt_to_pdb_by_adt',
	'clean_pdb_for_protein', 'compare_versions'
]

class NewPdbWriter(PdbWriter):
	def write_string(self, atoms):
		try:
			self.write("\\/*&^%$#@!><|", atoms, records=['ATOM', 'HETATM', 'CONECT'])
		except:
			pass

		lines = []
		for rec in self.PDBRECORDS:
			if rec in self.recordsToWrite:
				recLine = self.recordsToWrite[rec]
				if type(recLine) is list:
					lines.extend(recLine)
				else:
					lines.append(recLine)

		return ''.join(lines)

class AttrDict(dict):
	def __getattr__(self, attr):
		try:
			return self[attr]
		except KeyError:
			raise AttributeError(attr)

	def __setattr__(self, attr, val):
		self[attr] = val

	def deep_copy(self):
		new = self.__class__()

		for k, v in self.items():
			new[k] = v

		return new

def fetch_url(url):
	try:
		content = urlopen(url).read().decode()

		if 'sorry' in content:
			raise HTTPError()

		return content

	except HTTPError:
		return None

def convert_dimension_to_coordinates(x, y, z, cx, cy, cz, spacing):
	spacing = float(spacing)
	
	x_size = x * spacing
	y_size = y * spacing
	z_size = z * spacing

	x_half = x_size/2
	y_half = y_size/2
	z_half = z_size/2

	min_points = [cx-x_half, cy-y_half, cz-z_half]
	max_points = [cx+x_half, cy+y_half, cz+z_half]

	return (min_points, max_points)

def convert_coordinates_to_dimension(points, spacing):
	[(xmin, ymin, zmin), (xmax, ymax, zmax)] = points
	x_size = xmax - xmin
	y_size = ymax - ymin
	z_size = zmax - zmin

	x = int(x_size/spacing)
	y = int(y_size/spacing)
	z = int(z_size/spacing)

	if x % 2 != 0:
		x -= 1

	if y % 2 != 0:
		y -= 1

	if z % 2 != 0:
		z -= 1

	cx = round(xmin + x_size/2, 3)
	cy = round(ymin + y_size/2, 3)
	cz = round(zmin + z_size/2, 3)

	x = 126 if x > 126 else x
	y = 126 if y > 126 else y
	z = 126 if z > 126 else z

	return (x, y, z, cx, cy, cz)

def get_dimension_from_pdb(pdb_str, spacing):
	obc = openbabel.OBConversion()
	obc.SetInFormat('pdb')
	mol = openbabel.OBMol()
	obc.ReadString(mol, pdb_str)
	atoms = openbabel.OBMolAtomIter(mol)

	x_coords = []
	y_coords = []
	z_coords = []

	for atom in atoms:
		x_coords.append(atom.x())
		y_coords.append(atom.y())
		z_coords.append(atom.z())

	points = [
		(min(x_coords), min(y_coords), min(z_coords)),
		(max(x_coords), max(y_coords), max(z_coords))
	]

	return convert_coordinates_to_dimension(points, spacing)

def draw_gridbox(cmd, data):
	cmd.draw_box(
		points = convert_dimension_to_coordinates(
			data.x, data.y, data.z,
			data.cx, data.cy, data.cz,
			data.spacing
		),
		show_face = data.show_face,
		show_edge = data.show_edge,
		use_line = data.use_line,
		use_cylinder = data.use_cylinder,
		opacity = data.opacity,
		edge_width = data.edge_width,
		edge_color = data.edge_color,
		bg_x = data.bg_x,
		bg_y = data.bg_y,
		bg_z = data.bg_z
	)

#def generate_complex_pdb(*args):
#	return ''.join(args)

def generate_complex_pdb(receptor_pdb, ligand_pdb):
	complex_lines = []
	no_tre = True
	atom_num = 0

	for line in receptor_pdb.split('\n'):
		if line.startswith(('ATOM', 'HETATM', 'CRYST1')):
			complex_lines.append(line)
		elif line.startswith('TRE'):
			complex_lines.append(line)
			no_tre = False

		if line.startswith(('ATOM', 'HETATM')):
			num = int(line[6:11].strip())

			if num > atom_num:
				atom_num = num

	if no_tre:
		complex_lines.append('TRE   ')

	#if the atom number in ligand pdb is not sorted
	#to keep right atom order
	#get minimum atom number from ligand pdb
	ligand_lines = ligand_pdb.split('\n')
	min_num = 100000
	for line in ligand_lines:
		if line.startswith(('ATOM', 'HETATM')):
			num = int(line[6:11].strip())

			if num < min_num:
				min_num = num

	num_mapping = {}
	for line in ligand_lines:
		if line.startswith(('ATOM', 'HETATM')):
			line_chars = list(line)

			if line.startswith('ATOM'):
				line_chars[0:6] = list('HETATM')

			#renumber atom or hetatm
			#current atom number in ligand pdb
			curr_num = int(line[6:11].strip())
			new_num = atom_num + curr_num - min_num + 1
			line_chars[6:11] = list(str(new_num).rjust(5, ' '))
			complex_lines.append(''.join(line_chars))
			num_mapping[curr_num] = new_num

		elif line.startswith('CONECT'):
			line_chars = list(line)

			start = 6
			end = 11

			while 1:
				num_chars = line[start:end].strip()

				if not num_chars:
					break

				new_num = num_mapping[int(num_chars)]
				line_chars[start:end] = list(str(new_num).rjust(5, ' '))

				start = end
				end += 5

			complex_lines.append(''.join(line_chars))

	if complex_lines:
		complex_lines.append('END')

	return '\n'.join(complex_lines)

"""
def assign_bond_orders_from_origin(origin_file, pose_string):
	origin_format = os.path.splitext(origin_file)[1]

	if origin_format == '.pdb':
		template = Chem.MolFromPDBFile(origin_file)

	elif origin_format == '.mol2':
		template = Chem.MolFromMol2File(origin_file)

	elif origin_format == '.mol':
		template = Chem.MolFromMolFile(origin_file)

	elif origin_format == '.sdf':
		for template in Chem.SDMolSupplier(origin_file):
			pass

	with open('pose.pdb', 'w') as fw:
		fw.write(pose_string)

	docked_pose = Chem.MolFromPDBFile('pose.pdb')

	fixed_pose = AllChem.AssignBondOrdersFromTemplate(template, docked_pose)

	return Chem.MolToPDBBlock(fixed_pose)
"""

def convert_pdbqt_to_pdb_by_adt(origin_file, pdbqt, as_string=False):
	if as_string:
		mols = Read(alllines=pdbqt, dataformat='pdbqt')
	else:
		mols = Read(pdbqt)

	mol = mols[0]
	mol.buildBondsByDistance()
	mol.allAtoms.number = list(range(1, len(mol.allAtoms)+1))

	writer = NewPdbWriter()
	res = writer.write_string(mol.allAtoms)

	#correct = assign_bond_orders_from_origin(origin_file, res)

	return res

def convert_pdbqt_to_pdb(pdbqt, as_string=True):
	obc = openbabel.OBConversion()
	obc.SetInAndOutFormats('pdbqt', 'pdb')
	mol = openbabel.OBMol()

	if as_string:
		obc.ReadString(mol, pdbqt)
	else:
		obc.ReadFile(mol, pdbqt)

	return obc.WriteString(mol)

def convert_string_to_pdb(mol_str, mol_fmt):
	obc = openbabel.OBConversion()
	obc.SetInAndOutFormats(mol_fmt, 'pdb')
	mol = openbabel.OBMol()
	obc.ReadString(mol, mol_str)
	return obc.WriteString(mol)

def convert_other_to_pdbqt(infile, informat, outfile):
	obc = openbabel.OBConversion()
	obc.SetInAndOutFormats(informat, "pdbqt")
	mol = openbabel.OBMol()
	obc.ReadFile(mol, infile)

	non_bond = 0

	for atom in openbabel.OBMolAtomIter(mol):
		flag = 0
		for bond in openbabel.OBAtomBondIter(atom):
			flag = 1
			break

		if flag == 0:
			non_bond += 1
			

	print(non_bond)


	#correct for ph
	mol.CorrectForPH()

	#add hydrogens
	mol.AddHydrogens()
	#mol.AddPolarHydrogens()

	cmodel = openbabel.OBChargeModel.FindType('gasteiger')
	cmodel.ComputeCharges(mol)

	#set to be rigid
	obc.AddOption('r')
	obc.AddOption('x')
	#obc.AddOption('h')
	obc.AddOption('b')
	obc.AddOption('p')

	obc.WriteFile(mol, outfile)

def load_molecule_from_file(mol_file, mol_format):
	obc = openbabel.OBConversion()
	obc.SetInFormat(mol_format)
	mol = openbabel.OBMol()
	obc.ReadFile(mol, mol_file)
	return mol

def get_atom_types_from_pdbqt(pdbqt_file):
	atom_types = set()
	with open(pdbqt_file) as fh:
		for line in fh:
			if not line.startswith(('ATOM', 'HETATM')):
				continue

			cols = line.strip().split()

			atom_types.add(cols[-1])

	return sorted(atom_types)

def get_molecule_center_from_pdbqt(pdbqt_file):
	c = 0
	x = 0
	y = 0
	z = 0
	with open(pdbqt_file) as fh:
		for line in fh:
			if not line.startswith(('ATOM', 'HETATM')):
				continue

			cols = line.strip().split()
			c += 1 
			x += float(cols[6])
			y += float(cols[7])
			z += float(cols[8])

	x = round(x/c, 3)
	y = round(y/c, 3)
	z = round(z/c, 3)

	return x, y, z

def time_format(seconds):
	if seconds:
		t = time.localtime(seconds)
		return time.strftime("%Y-%m-%d %H:%M:%S", t)
	else:
		return 'N/A'

def time_elapse(start, stop):
	if not stop:
		return 'N/A'

	seconds = stop - start

	if not seconds:
		return '0s'

	h = int(seconds // 3600)
	m = int(seconds % 3600 // 60)
	s = int(seconds % 60)

	ts = []
	if h:
		ts.append("{}h".format(h))

	if m:
		ts.append("{}m".format(m))

	if s:
		ts.append("{}s".format(s))

	return ' '.join(ts)

def memory_format(size):
	for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
		if size < 1024:
			break

		size /= 1024

	return "{:.2f}{}".format(size, unit)

def convert_ki_to_log(ki_str):
	if not ki_str:
		return ''

	ki, unit = ki_str.split()
	ki = float(ki)

	scales = {
		'M': 0, 'mM': 3, 'uM': 6, 'nM': 9, 'pM': 12,
		'fM': 15, 'aM': 18, 'zM': 21, 'yM': 24
	}
	ki = ki/math.pow(10, scales[unit])
	return round(math.log10(ki), 3)

def convert_ki_to_str(ki):
	scales = [('M', 0), ('mM', 3), ('uM', 6), ('nM', 9), ('pM', 12),
		('fM', 15), ('aM', 18), ('zM', 21), ('yM', 24)]

	for unit, scale in scales:
		ck = ki * math.pow(10, scale)

		if ck >= 1:
			return "{} {}".format(round(ck,2), unit)

def convert_energy_to_ki(energy):
	R = 1.9871917
	T = 298.15
	ki = math.exp((energy*1000)/(R*T))
	return ki

def get_molecule_information(mol_file, from_string=False, mol_name=None, mol_format=None):
	if not from_string:
		mol_name, mol_format = os.path.splitext(os.path.basename(mol_file))
		mol_format = mol_format.lstrip('.').lower()

	if mol_format in ['pdb', 'mol', 'mol2', 'sdf']:
		out_format = mol_format

		if from_string:
			mol_content = mol_file
		else:
			with open(mol_file, encoding='utf-8') as fh:
				mol_content = fh.read()

	else:
		out_format = 'pdb'
		mol_content = None

	obc = openbabel.OBConversion()
	obc.SetInAndOutFormats(mol_format, out_format)
	mol = openbabel.OBMol()

	if from_string:
		obc.ReadString(mol, mol_file)
	else:
		obc.ReadFile(mol, mol_file)

	if mol_content is None:
		mol_content = obc.WriteString(mol)
	
	descriptor = openbabel.OBDescriptor.FindType('logP')
	log_p = descriptor.Predict(mol)

	return AttrDict(
		name = mol_name,
		format = out_format,
		atoms = mol.NumAtoms(),
		bonds = mol.NumBonds(),
		hvyatoms = mol.NumHvyAtoms(),
		residues = mol.NumResidues(),
		rotors = mol.NumRotors(),
		formula = mol.GetFormula(),
		energy = mol.GetEnergy(),
		weight = mol.GetMolWt(),
		logp = log_p,
		content = mol_content
	)

def get_molecule_residues(mol_str, mol_fmt):
	obc = openbabel.OBConversion()
	obc.SetInFormat(mol_fmt)
	mol = openbabel.OBMol()
	obc.ReadString(mol, mol_str)

	for res in openbabel.OBResidueIter(mol):
		yield (str(res.GetIdx()), res.GetChain(), res.GetName(),
			str(res.GetNum()), str(res.GetNumAtoms()))

def get_residue_bonds(mol_str, mol_fmt, res_idx):
	obc = openbabel.OBConversion()
	obc.SetInFormat(mol_fmt)
	mol = openbabel.OBMol()
	obc.ReadString(mol, mol_str)

	for bond in openbabel.OBMolBondIter(mol):
		begin_atom = bond.GetBeginAtom()
		end_atom = bond.GetEndAtom()
		begin_res = begin_atom.GetResidue()
		end_res = end_atom.GetResidue()
		begin_idx = begin_res.GetIdx()
		end_idx = end_res.GetIdx()

		if res_idx == begin_idx or res_idx == end_idx:
			begin_aid = begin_res.GetAtomID(begin_atom).strip()
			end_aid = end_res.GetAtomID(end_atom).strip()
			atom = "{}-{}".format(begin_aid, end_aid)

			yield (atom, str(round(bond.GetLength(), 3)), bond.IsAromatic(),
				bond.IsRotor(), bond.IsAmide())

def ligand_efficiency_assessment(pdb_str, energy, ki=None):
	if ki is None:
		ki = convert_energy_to_ki(energy)
		logki = round(math.log10(ki), 3)
		ki = convert_ki_to_str(ki)
	else:
		logki = convert_ki_to_log(ki)

	if pdb_str:
		obc = openbabel.OBConversion()
		obc.SetInFormat("pdb")
		mol = openbabel.OBMol()
		obc.ReadString(mol, pdb_str)
		ha = mol.NumHvyAtoms()
		mw = mol.GetMolWt()

		#calculate ligand efficiency
		le = round(energy/ha * -1, 3)

		#calculate size-independent ligand efficiency
		sile = round(energy/pow(ha, 0.3) * -1, 3)

		#calculate logP
		des = openbabel.OBDescriptor.FindType('logP')
		logp = des.Predict(mol)

		#calculate ligand lipophilic efficiency
		if logki:
			lle = round(-1*logki - logp, 3)
		else:
			lle = None

		#calculate fit quality
		le_scale = 0.0715 + 7.5328/ha + 25.7079/math.pow(ha,2) - 361.4722/math.pow(ha, 3)
		fq = round(le/le_scale, 3)

		#calculate ligand efficiency lipophilic price
		lelp = round(logp/le, 3)

		return (logki, le, sile, fq, lle, lelp, ki)
	else:
		return (logki, None, None, None, None, None, ki)

def get_complex_interactions(poses, work_dir, active_sites):
	interactions = {
		'binding_site': [],
		'hydrogen_bond': [],
		'hydrophobic_interaction': [],
		'water_bridge': [],
		'salt_bridge': [],
		'pi_stacking': [],
		'pi_cation': [],
		'halogen_bond': [],
		'metal_complex': []
	}

	for i, pose in enumerate(poses):
		compound = pose[-1]
		poses[i].append('')
		
		if not compound:
			continue

		mol = PDBComplex()
		mol.output_path = work_dir
		mol.load_pdb(compound, as_string=True)
		mol.analyze()

		for site in mol.interaction_sets:
			interactions['binding_site'].append([None, i, site])
			s = mol.interaction_sets[site]

			site = "{}:{}".format(i, site)

			#hydrogen bonds
			for hb in s.hbonds_pdon + s.hbonds_ldon:
				residue = "{}:{}:{}".format(hb.reschain, hb.restype, hb.resnr)

				if residue in active_sites:
					is_active_site = 1
					interact = "hydrogen_bond:{}".format(residue)

					if poses[i][-1]:
						if interact not in poses[i][-1]:
							poses[i][-1] = "{};{}".format(poses[i][-1], interact)

					else:
						poses[i][-1] = interact

				else:
					is_active_site = 0

				interactions['hydrogen_bond'].append([None, site,
					hb.reschain, hb.resnr, hb.restype,
					"{:.2}".format(hb.distance_ah),
					"{:.2}".format(hb.distance_ad),
					"{:.2}".format(hb.angle),
					'Yes' if hb.protisdon else 'No',
					'Yes' if hb.sidechain else 'No',
					"{} [{}]".format(hb.d_orig_idx, hb.dtype),
					"{} [{}]".format(hb.a_orig_idx, hb.atype),
					is_active_site
				])

			#hydrophobic interactions
			for hc in s.hydrophobic_contacts:
				residue = "{}:{}:{}".format(hc.reschain, hc.restype, hc.resnr)

				if residue in active_sites:
					is_active_site = 1
					interact = "hydrophobic_interaction:{}".format(residue)

					if poses[i][-1]:
						if interact not in poses[i][-1]:
							poses[i][-1] = "{};{}".format(poses[i][-1], interact)

					else:
						poses[i][-1] = interact

				else:
					is_active_site = 0

				interactions['hydrophobic_interaction'].append([None, site,
					hc.reschain, hc.resnr, hc.restype,
					"{:.2}".format(hc.distance),
					hc.ligatom_orig_idx,
					hc.bsatom_orig_idx,
					is_active_site
				])

			#water bridges
			for wb in s.water_bridges:
				residue = "{}:{}:{}".format(wb.reschain, wb.restype, wb.resnr)

				if residue in active_sites:
					is_active_site = 1
					interact = "water_bridge:{}".format(residue)

					if poses[i][-1]:
						if interact not in poses[i][-1]:
							poses[i][-1] = "{};{}".format(poses[i][-1], interact)

					else:
						poses[i][-1] = interact

				else:
					is_active_site = 0

				interactions['water_bridge'].append([None, site,
					wb.reschain, wb.resnr, wb.restype,
					"{:.2}".format(wb.distance_aw),
					"{:.2}".format(wb.distance_dw),
					"{:.2}".format(wb.d_angle),
					"{:.2}".format(wb.w_angle),
					'Yes' if wb.protisdon else 'No',
					"{} [{}]".format(wb.d_orig_idx, wb.dtype),
					"{} [{}]".format(wb.a_orig_idx, wb.atype),
					wb.water_orig_idx,
					is_active_site
				])

			#salt bridges
			for sb in s.saltbridge_lneg + s.saltbridge_pneg:
				residue = "{}:{}:{}".format(sb.reschain, sb.restype, sb.resnr)

				if residue in active_sites:
					is_active_site = 1
					interact = "salt_bridge:{}".format(residue)

					if poses[i][-1]:
						if interact not in poses[i][-1]:
							poses[i][-1] = "{};{}".format(poses[i][-1], interact)

					else:
						poses[i][-1] = interact

				else:
					is_active_site = 0

				if sb.protispos:
					group = sb.negative.fgroup
					ligand_atom_ids = ','.join(str(x) for x in sb.negative.atoms_orig_idx)
					protein_atom_ids = ','.join(str(x) for x in sb.positive.atoms_orig_idx)
				else:
					group = sb.positive.fgroup
					ligand_atom_ids = ','.join(str(x) for x in sb.positive.atoms_orig_idx)
					protein_atom_ids = ','.join(str(x) for x in sb.negative.atoms_orig_idx)

				interactions['salt_bridge'].append([None, site,
					sb.reschain, sb.resnr, sb.restype,
					"{:.2}".format(sb.distance),
					'Yes' if sb.protispos else 'No',
					group.capitalize(),
					ligand_atom_ids,
					is_active_site
					#protein_atom_ids
				])

			#pi-stacking
			for ps in s.pistacking:
				residue = "{}:{}:{}".format(ps.reschain, ps.restype, ps.resnr)

				if residue in active_sites:
					is_active_site = 1
					interact = "pi_stacking:{}".format(residue)

					if poses[i][-1]:
						if interact not in poses[i][-1]:
							poses[i][-1] = "{};{}".format(poses[i][-1], interact)

					else:
						poses[i][-1] = interact

				else:
					is_active_site = 0

				interactions['pi_stacking'].append([None, site,
					ps.reschain, ps.resnr, ps.restype,
					"{:.2}".format(ps.distance),
					"{:.2}".format(ps.angle),
					"{:.2}".format(ps.offset),
					ps.type,
					','.join(str(x) for x in ps.ligandring.atoms_orig_idx),
					is_active_site
					#','.join(str(x) for x in ps.proteinring.atoms_orig_idx)
				])

			#pi-cation
			for pc in s.pication_laro + s.pication_paro:
				residue = "{}:{}:{}".format(pc.reschain, pc.restype, pc.resnr)

				if residue in active_sites:
					is_active_site = 1
					interact = "pi_cation:{}".format(residue)

					if poses[i][-1]:
						if interact not in poses[i][-1]:
							poses[i][-1] = "{};{}".format(poses[i][-1], interact)

					else:
						poses[i][-1] = interact

				else:
					is_active_site = 0

				if pc.protcharged:
					ligand_atom_ids = ','.join(str(x) for x in pc.ring.atoms_orig_idx)
					protein_atom_ids = ','.join(str(x) for x in pc.charge.atoms_orig_idx)
					group = 'Aromatic'
				else:
					ligand_atom_ids = ','.join(str(x) for x in pc.charge.atoms_orig_idx)
					protein_atom_ids = ','.join(str(x) for x in pc.ring.atoms_orig_idx)
					group = pc.charge.fgroup

				interactions['pi_cation'].append([None, site,
					pc.reschain, pc.resnr, pc.restype,
					"{:.2}".format(pc.distance),
					"{:.2}".format(pc.offset),
					'Yes' if pc.protcharged else 'No',
					group.capitalize(),
					ligand_atom_ids,
					is_active_site
					#protein_atom_ids
				])

			#halogen bonds
			for ha in s.halogen_bonds:
				residue = "{}:{}:{}".format(ha.reschain, ha.restype, ha.resnr)

				if residue in active_sites:
					is_active_site = 1
					interact = "halogen_bond:{}".format(residue)

					if poses[i][-1]:
						if interact not in poses[i][-1]:
							poses[i][-1] = "{};{}".format(poses[i][-1], interact)

					else:
						poses[i][-1] = interact

				else:
					is_active_site = 0

				interactions['halogen_bond'].append([None, site,
					ha.reschain, ha.resnr, ha.restype,
					"{:.2}".format(ha.distance),
					"{:.2}".format(ha.don_angle),
					"{:.2}".format(ha.acc_angle),
					"{} [{}]".format(ha.don_orig_idx, ha.donortype),
					"{} [{}]".format(ha.acc_orig_idx, ha.acctype),
					is_active_site
				])

			#metal complexes
			for mc in s.metal_complexes:
				residue = "{}:{}:{}".format(mc.reschain, mc.restype, mc.resnr)

				if residue in active_sites:
					is_active_site = 1
					interact = "metal_complex:{}".format(residue)

					if poses[i][-1]:
						if interact not in poses[i][-1]:
							poses[i][-1] = "{};{}".format(poses[i][-1], interact)

					else:
						poses[i][-1] = interact

				else:
					is_active_site = 0

				interactions['metal_complex'].append([None, site,
					mc.reschain, mc.resnr, mc.restype,
					"{} [{}]".format(mc.metal_orig_idx, mc.metal_type),
					"{} [{}]".format(mc.target_orig_idx, mc.target_type),
					"{:.2}".format(mc.distance),
					mc.location,
					is_active_site
				])

	return interactions

#https://github.com/pharmai/plip/blob/master/plip/visualization/visualize.py
def interaction_visualize(plcomplex):
	#clear pymol viewer
	cmd.delete('all')
	cmd.reinitialize()

	vis = PyMOLVisualizer(plcomplex)

	pdbid = plcomplex.pdbid
	lig_members = plcomplex.lig_members
	chain = plcomplex.chain
	if config.PEPTIDES:
		vis.ligname = 'PeptideChain%s' % plcomplex.chain
	if config.INTRA is not None:
		vis.ligname = 'Intra%s' % plcomplex.chain

	ligname = vis.ligname
	hetid = plcomplex.hetid

	metal_ids = plcomplex.metal_ids
	metal_ids_str = '+'.join([str(i) for i in metal_ids])

	vis.set_initial_representations()

	#cmd.load(plcomplex.sourcefile)
	cmd.read_pdbstr(plcomplex.corrected_pdb, 'complex')
	cmd.frame(config.MODEL)
	current_name = cmd.get_object_list(selection='(all)')[0]

	cmd.set_name(current_name, pdbid)
	cmd.hide('everything', 'all')
	if config.PEPTIDES:
		cmd.select(ligname, 'chain %s and not resn HOH' % plcomplex.chain)
	else:
		cmd.select(ligname, 'resn %s and chain %s and resi %s*' % (hetid, chain, plcomplex.position))

	# Visualize and color metal ions if there are any
	if not len(metal_ids) == 0:
		vis.select_by_ids(ligname, metal_ids, selection_exists=True)
		cmd.show('spheres', 'id %s and %s' % (metal_ids_str, pdbid))

	# Additionally, select all members of composite ligands
	if len(lig_members) > 1:
		for member in lig_members:
			resid, chain, resnr = member[0], member[1], str(member[2])
			cmd.select(ligname, '%s or (resn %s and chain %s and resi %s)' % (ligname, resid, chain, resnr))

	cmd.show('sticks', ligname)
	cmd.color('myblue')
	cmd.color('myorange', ligname)
	cmd.util.cnc('all')
	if not len(metal_ids) == 0:
		cmd.color('hotpink', 'id %s' % metal_ids_str)
		cmd.hide('sticks', 'id %s' % metal_ids_str)
		cmd.set('sphere_scale', 0.3, ligname)
	cmd.deselect()

	vis.make_initial_selections()

	vis.show_hydrophobic()  # Hydrophobic Contacts
	vis.show_hbonds()  # Hydrogen Bonds
	vis.show_halogen()  # Halogen Bonds
	vis.show_stacking()  # pi-Stacking Interactions
	vis.show_cationpi()  # pi-Cation Interactions
	vis.show_sbridges()  # Salt Bridges
	vis.show_wbridges()  # Water Bridges
	vis.show_metal()  # Metal Coordination

	vis.refinements()

	vis.zoom_to_ligand()

	vis.selections_cleanup()

	vis.selections_group()
	vis.additional_cleanup()

	#show aa labels
	#cmd.set('label_color', 'white')
	#cmd.set('label_outline_color', 'grey')
	#cmd.set('float_labels', 'on')
	#cmd.set('label_position', (0,-1.5,0))
	cmd.label('n. CA and AllBSRes', '"%s%s%s" % (resn,resi,chain)')

def sdf_file_parser(sdf_file, name_prop):
	suppl = Chem.SDMolSupplier(sdf_file, sanitize=False,
		removeHs=False, strictParsing=False)

	for mol in suppl:
		if not mol:
			continue

		name = mol.GetProp(name_prop)
		content = Chem.SDWriter.GetText(mol, kekulize=False)
		yield (name, content)

def get_sdf_props(sdf_file):
	suppl = Chem.SDMolSupplier(sdf_file, sanitize=False,
		removeHs=False, strictParsing=False)

	for mol in suppl:
		if mol:
			return mol.GetPropNames()

def clean_pdb_for_protein(pdb_file):
	std_residues = [
		'CYS','ILE','SER','VAL','GLN','LYS','ASN',
		'PRO','THR','PHE','ALA','HIS','GLY','ASP',
		'LEU', 'ARG', 'TRP', 'GLU', 'TYR','MET',
		'HID', 'HSP', 'HIE', 'HIP', 'CYX', 'CSS'
	]

	lines = []
	with open(pdb_file) as fh:
		for line in fh:
			if line.startswith('ATOM'):
				if line[17:20] in std_residues:
					lines.append(line)

	return ''.join(lines)

def compare_versions(version1, version2):
	major1, minor1, patch1 = version1.split('.')
	major2, minor2, patch2 = version2.split('.')

	if int(major1) > int(major2):
		return True
	elif int(major1) < int(major2):
		return False

	if int(minor1) > int(minor2):
		return True
	elif int(minor1) < int(minor2):
		return False

	if int(patch1) > int(patch2):
		return True
	elif int(patch1) < int(patch2):
		return False

	return True

if __name__ == '__main__':
	flag = compare_versions('0.9.0', '1.0.0')
	print(flag)
