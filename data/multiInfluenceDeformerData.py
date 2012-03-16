import deformerData

class MultiInfluenceDeformerData( deformerData.DeformerData ):
	"""
	MultiInfluenceDeformerData class object.
	This class is derived directly from the base class deformerData, and should be
	the parent class for all other multiInfluence deformer data classes.
	"""
	def __init__(self,deformer=''):
		super(MultiInfluenceDeformerData, self).__init__(deformer)
		self.influenceData = {}
