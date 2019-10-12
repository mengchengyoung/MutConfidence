#!/annoroad/data1/bioinfo/PMO/yangmengcheng/SoftWare/Anaconda3-5.3.1/envs/ML/bin/python3
def get_pon():
    pon_file = '/annoroad/data1/bioinfo/PROJECT/Commercial/Medical/Leukemia/database/Leu_V3/PON.filter'
    pon = dict()
    min_depth = 50
    with open(pon_file) as f:
        line = f.readline().strip()
        while line:
            chr, loc, ref, alt, sample_per, sample_number, per_mean, per_std, dep_mean, dep_std = line.split('\t')
            sample_per , sample_number, per_mean,  per_std, dep_mean, dep_std = (float(sample_per), float(sample_number), 
                                                                                float(per_mean), float(per_std), float(dep_mean),
                                                                                float(dep_std))
            key = "{chr}{loc}{ref}{alt}".format(chr=chr, loc=loc, ref=ref, alt=alt)
            if (sample_per>0.8) and (dep_mean-dep_std > 10):
                pon[key] = per_mean+3*per_std
            elif dep_mean <50:
                line = f.readline().strip()
                continue
            elif sample_per>0.4:
                pon[key] = per_mean+3*per_std
            elif sample_per>0.2:
                pon[key] = per_mean+2*per_std
            elif sample_per>0.1:
                pon[key] = per_mean+per_std
            else:
                pon[key] = per_mean+per_std/2
            line = f.readline().strip()
        return pon

_PON=get_pon()
class VCF():
    '''
    class for VCF file 
    '''
    def __init__(self, vcf_file):
        self.filename = vcf_file
        self.iterator = self.get_iterator()
        self.head = list()
        self.pon = _PON 
    @property
    def vcfformat(self):
        """
        override this function if necessary
        """
        pass
    
    @property
    def get_sites(self):
        _sites = list()
        for i in self.iterator:
            """
            override the filter function if necessary
            """
            if  not self.filter_format(i['format']):
                continue
                
            site = Site(i)
            
            if not self.filter_site(site):
                continue
            
            _sites.append(site.infos)
        return _sites

    def get_iterator(self):
        """
        override this file if the vcfformat is not VCFv4.2
        at least yiled a site
        """
        print(self.filename)
        with open(self.filename) as f:
            line = f.readline().strip()
            while line:
                if not line.startswith('#'):
                    line = line.split('\t')
                    site = dict(reference=line[0], pos=int(line[1]), ref=line[3], alt=line[4], FILTER=line[6], format=line[-1])
                    yield site
                else:
                    self.head.append(line)
                line = f.readline().strip()
    
    def filter_format(self, format):
        """
        override if want to keep some site that has an different format or just abandon
        """
        if len(format.split(':')) != 9:
            return False
        return True

    def filter_site(self, site):
        """
            filter: low frequency == 0
                    indel(temporary)
        """
        site = site.infos
        if site['frequency'] == 0:
            return False
        if site['type'] == 'indel':
            return False
        return True 

class Site():
    '''
        class for a single site
    '''
    def __init__(self, site):
        self.site = site
        self.format_dict = self.get_format()
        self.pon = _PON
        self.infos = dict(type=self.get_type,
                          frequency=self.get_frequency,
                          depth=self.get_depth,
                          reference=None, # chromosome
                          pos=None, # 1-base
                          ref=None,
                          alt=None,
                          GT=None,
                          AD=None,
                          AF=None,
                          ALT_F1R2=None,
                          ALT_F2R1=None,
                          FOXOG=None,
                          NORMAL=self.get_NORMAL,
                          Tlodfstar=self.get_Tlodfstar,
                          PONFilter=self.get_PONFilter,
                          QSS=None,
                          REF_F1R2=None,
                          REF_F2R1=None)
        self.init()

    @property
    def get_type(self):
        '''
        Get type of one site
        '''
        ref = self.site['ref']
        alt = self.site['alt']
        return 'indel' if len(ref)-len(alt) != 0 else 'snp'

    def get_format(self):
        """
        there may be some unstandard format info in some files
        some sites got PID filed and so on..
        """
        format_ = self.site['format'].split(':') 
        format_dict = dict()
        format_dict['GT'] = format_[0]
        format_dict['AD'] = format_[1]
        format_dict['AF'] = format_[2]
        format_dict['ALT_F1R2'] = format_[3]
        format_dict['ALT_F2R1'] = format_[4]
        format_dict['FOXOG'] = format_[5]
        format_dict['QSS'] = format_[6]
        format_dict['REF_F1R2'] = format_[7]
        format_dict['REF_F2R1'] = format_[8]
        return format_dict

    @property
    def get_frequency(self):
        '''
        return Frequency of one site
        '''
        format_AD = self.format_dict['AD'].split(',')
        alt_num = int(format_AD[1])
        ref_num = int(format_AD[0])
        return float("{:.2f}".format(alt_num/(ref_num+alt_num)))
    
    @property
    def get_depth(self):
        """
        return depth of one site
        """
        format_AD = self.format_dict['AD'].split(',')
        alt_num = int(format_AD[1])
        ref_num = int(format_AD[0])
        return alt_num+ref_num

    @property
    def get_NORMAL(self):
        """
        encoding normal flag to binary
        """
        if 'panel_of_normals' in self.site['FILTER']:
            return 0
        else:
            return 1

    @property
    def get_Tlodfstar(self):
        """
        encoding Tlodfstar flag to binary
        """
        if "t_lod_fstar" in self.site['FILTER']:
            return 1
        else:
            return 0
    
    @property
    def get_PONFilter(self):
        key = "{reference}{pos}{ref}{alt}".format(reference=self.site['reference'], pos=self.site['pos'], ref=self.site['ref'], alt=self.site['alt'])
        pon = self.pon.get(key, False)
        if pon and self.get_frequency>pon :
            return 0
        elif not pon:
            return 0
        else:
            return 1

    def init(self):
        self.infos = {**self.infos, **self.format_dict}
        self.infos = {**self.infos, **self.site}
    
def test():
    vcf = VCF('/annoroad/data1/bioinfo/PROJECT/Commercial/Medical/Leukemia/data/Commercial_V3/HB_828_2019081709110848/result/HB15ANSY00185-1-I20/Variant/SNP-INDEL_MT/HB15ANSY00185-1-I20-SNP.vcf')
    print(vcf.get_sites[0].infos)
    print(vcf.head[0])
    print(vcf.filename)
    print(vcf.get_sites) 
if __name__ == "__main__":
    test()
