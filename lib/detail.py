#!/annoroad/data1/bioinfo/PMO/yangmengcheng/SoftWare/Anaconda3-5.3.1/bin/python

import pysam 

_reference_file = '/annoroad/data1/bioinfo/PMO/zhoumiao/public/ref/hg19.fa'
_ponfilter = '/annoroad/data1/bioinfo/PROJECT/Commercial/Medical/Leukemia/database/Leu_V3/PON.filter'

class BaseError(Exception):
    pass

class Detail():
    """
    This class use to extract info from bamfile for specified position
    """
    def __init__(self, AlignmentFile, Base=None):
        self.AlignmentFile = AlignmentFile
        self._Base = Base
        #self.position = dict(contig=self.Base['chr'], start=self.Base['pos'], stop=self.Base['pos']+1)
        #self.AF = self.Base['frequency']
        self._hg19 = pysam.FastaFile(_reference_file)

    @property
    def Base(self):
        return self._Base

    @Base.setter
    def Base(self, base):
        """
        override this functin to check the base
        """
        self._Base = base 
        self.column_quality_list = list()
        self.insert_list = list()
        self.target_column = None
        self.strand_list = list() # all the base mapped at the position
        self.mapping_quality_list = list()
        self.init()

    @property
    def get_GC(self):
        flank = 37
        region = dict(reference = self.Base['reference'], 
                      start = self.Base['pos']-flank,
                      end = self.Base['pos']+flank)
        seq = self._hg19.fetch(**region)

        GC = (seq.count('C') + seq.count('G'))/(len(seq))
        return GC

    @property
    def get_strand_bias(self):
        #print(self.strand_list)
        reverse = self.strand_list.count(True)+1
        forward = self.strand_list.count(False)+1
        bias = min(reverse/forward, forward/reverse)
        return bias 

    @property
    def get_insert_average(self):
        """
        assume that there isn't adpter polutted read, so we 
        """
        insert_list = [abs(int(i)) for i in self.insert_list] 
        avg = sum(insert_list)/len(insert_list)
        return avg

    @property
    def get_Pon(self):
        pass
    
    @property
    def get_base_quality(self):
        avg = sum(self.column_quality_list)/len(self.column_quality_list)
        return avg 

    @property
    def get_mapping_quality(self):
        mapping_list = [i for i in self.mapping_quality_list if isinstance(i, int)]
        avg = sum(mapping_list)/len(mapping_list)
        return avg

    @property
    def region(self):
        if bool(self.Base):
            return dict(reference=self.Base['reference'],
                        start=int(self.Base['pos']), 
                        end=int(self.Base['pos'])+1)
        else:
            raise BaseError('Base not set')
    
    def filter(self, AlignedSegment):
        """
        override filter function if neccecsary
        """
        if AlignedSegment.is_duplicate:
            return False
        return True

    def init(self):
        flank = 1
        region = dict(reference = self.Base['reference'],
                      start = self.Base['pos']-flank,
                      end = self.Base['pos']+flank )
        ps = self.AlignmentFile.pileup(**region) # 0-base
        for i,column in enumerate(ps):
            if column.reference_pos == (self.Base['pos']-1): # 0-base
                # get the distributioni of quality 
                self.column_quality_list = column.get_query_qualities()

                for Pread in column.pileups:
                    if not self.filter(Pread.alignment):
                        continue
                    self.insert_list.append(Pread.alignment.template_length)
                    self.strand_list.append(Pread.alignment.is_reverse)
                    self.mapping_quality_list.append(Pread.alignment.mapping_quality) 
    
