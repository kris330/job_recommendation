import cython
from libc.stdint cimport uint32_t, uint64_t, int64_t, float
from libcpp.vector cimport vector
from libcpp.string cimport string as std_string
from libcpp.utility cimport pair

cdef extern from "string.h": 
    char *strcpy(char *dest, char *src)

cdef extern from "jobrecmd.h":
    ctypedef unsigned int u_int

    ctypedef enum jrdata_type_t:
        _title
        _info

    ctypedef struct jrword_t:
      uint64_t word_id    
      u_int word_weight

    ctypedef struct jrout_t:
      jrword_t title_term_weights[10]   #word_id == 10
      u_int title_term_num
      jrword_t info_term_weights[10]
      u_int info_term_num

    cdef cppclass jrdict_t:
      pass

    ctypedef struct jdentity2_t:
      jrword_t title_term_weights[11]   #word_id == 10
      u_int title_term_num
      jrword_t info_term_weights[11]
      u_int info_term_num

    #ctypedef pair[std_string, u_int] item
  
    cdef cppclass jrdata_t:
        #cdef pair[std_string, u_int] item
        vector[pair[std_string, u_int]]  title_term_weights
        vector[pair[std_string, u_int]]  info_term_weights
        pass

    cdef jrout_t *jr_create_out(unsigned int max_jds_num)
    cdef void jr_destroy_out(jrout_t *& pout)

    cdef void jr_destroy_model(jrdict_t *&pdict)
    cdef int jr_load_inner_model(jrdict_t *pdict, const char *model_dir)

    cdef int jr_append_jrdata(jrdata_t &jrbuf, jrdata_type_t type, const char *info, unsigned int weight)
    cdef int jr_reset_jrdata(jrdata_t &jrd)
    cdef int jr_reset_poutdata(jrout_t *pout) 
    
    cdef int jrdata_to_keywords(jrdict_t *pdict, jrout_t *pout, jrdata_t &jrbuf) 
    cdef unsigned int jr_calc_cv_jd(jdentity2_t *pentity, jrout_t *pout)

cdef class Jobrmd(object):
    cdef jrdict_t* _dict
    cdef jrout_t* _out
    cdef jrdata_t _buf

    def __init__(self):
      self._dict = new jrdict_t()
      self._out = jr_create_out(5000000)
      pass
    
    def __del__(self):
      jr_destroy_model(self._dict)
      jr_destroy_out(self._out)

    cpdef int load(self, const char* dict_path):
      return jr_load_inner_model(self._dict, dict_path)
    
    cpdef keywords(self, infos):
      jr_reset_jrdata(self._buf)
      jr_reset_poutdata(self._out)
     
      for info in infos:
        info_type, info_txt, info_weight = info
        if type(info_txt) == unicode:
          info_txt = info_txt.encode('utf-8')
        jr_append_jrdata(self._buf, <jrdata_type_t>info_type, info_txt, info_weight)

      jrdata_to_keywords(self._dict, self._out, self._buf)
      # get keys
      #for term in self._buf.title_term_weights:
      #  print term
      return self._buf.title_term_weights, self._buf.info_term_weights
    
cpdef int calc_score(src, det):
    """
      1 input src = ([(term_id, weight)], [(term, weight)])
      2 only the 1st 10 terms. ignore weighting
    """
    cdef jrout_t jr_det
    cdef jdentity2_t jr_src

    # build src
    title, info = src
    jr_src.title_term_num = min(len(title), 10)
    for i in range(0, jr_src.title_term_num):
        jr_src.title_term_weights[i].word_id = title[i][0]
        jr_src.title_term_weights[i].word_weight = title[i][1]
        #print 'jr_src', 

    jr_src.info_term_num = min(len(info), 10)
    for i in range(0, jr_src.info_term_num):
        jr_src.info_term_weights[i].word_id = info[i][0]
        jr_src.info_term_weights[i].word_weight = info[i][1]
    
    # build det
    title, info = det
    jr_det.title_term_num = min(len(title), 10)
    for i in range(0, jr_det.title_term_num):
        jr_det.title_term_weights[i].word_id = title[i][0]
        jr_det.title_term_weights[i].word_weight = title[i][1]

    jr_det.info_term_num = min(len(info), 10)
    for i in range(0, jr_det.info_term_num):
        jr_det.info_term_weights[i].word_id = info[i][0]
        jr_det.info_term_weights[i].word_weight = info[i][1]
    #dprint jr_src.title_term_num, jr_src.info_term_num, jr_det.title_term_num,  jr_det.info_term_num
    n = jr_calc_cv_jd(&jr_src, &jr_det)
    #print n
    return n

def addtest(a,b):
    cdef float c=a+b
    return c


# -*- end of file -*-
