/***************************************************************************
 * 
 * $Id$ 
 * 
 **************************************************************************/
 
 
 
/**
 * jobrecmd.h ~ 2014/03/07 21:45:52
 * @version $Revision$ 
 * @description 
 *  
 **/



#ifndef  __JOBRECMD_H_
#define  __JOBRECMD_H_
#include "segdef.h"
#include "termkword.h"
#include <string>
#include <vector>
#include "stdint.h"



typedef unsigned int u_int;

/**
 * ��ر���
 */
const u_int JR_STACK_SIZE = 512;	
const u_int JR_INFO_MAX_SIZE = 102400;
const u_int JRC_PAIR_MAX_NUM = 10;
const u_int JR_MAX_KEYWORDS_NUM = 10;
const u_int JR_NAME_LENGTH = 64;



/**
 * @brief �������ݵĸ�ʽ��Ŀǰ��ʱ����Ϊ���֣�ְλ���߼����ı���(_title) �� ����������Ϣ
 */
typedef enum JRDATA_TYPE_T{
	_title=0,
	_info=1,
}jrdata_type_t;


/**
 * @brief ���� ְλ �������ݵĽṹ�壻
 */
typedef struct JR_DATA_T{
	char name[JR_NAME_LENGTH];		  /**<   jd cv ��Ӧ���ļ���(hashֵ)     */
	char title[JR_STACK_SIZE];		  /**<   jdְλ�� ���� cv��ְ������    */

	std::vector<std::pair<std::string, u_int > > info;		  /**<  jd cv ���ַ�title�Ľṹ����Ϣ�Լ���Ӧ��Ȩ��     */

	std::vector<std::pair<std::string, u_int > > title_term_weights;
	std::vector<std::pair<std::string, u_int > > info_term_weights;

}jrdata_t;


/**
 * @brief �ؼ�����Ϣ�� 
 */
typedef struct JR_WORD_T{
	uint64_t word_id;		  /**<  �ؼ���ID      */
	u_int word_weight;		  /**<  �ؼ���Ȩ��      */
}jrword_t;


/**
 * @brief ÿ�������Ľṹ����Ϣ
 */
typedef struct JD_ENTITY_T{
	char jdname[JR_NAME_LENGTH];		  /**<  ÿ��������hash id �ַ���ֵ      */

	u_int infot_begin;		  /**<  jd info�ؼ�����pdict->info_term_weights�е���ʼλ��      */
	u_int infot_len;  /**<  jd info�ؼ�����pdict->info_term_weights�еĳ���ֵ     */

	u_int titlet_begin;	  /**<  jd title �ؼ�����pdict->info_term_weights�е���ʼλ��      */
	u_int titlet_len; /**<  jd title �ؼ�����pdict->info_term_weights�еĳ���ֵ     */

}jdentity_t;




typedef struct JD_ENTITY_T2{
	char jdname[JR_NAME_LENGTH];		  /**< jd name  */
	jrword_t title_term_weights[JR_MAX_KEYWORDS_NUM+1];
	u_int title_term_num;
	jrword_t info_term_weights[JR_MAX_KEYWORDS_NUM+1];
	u_int info_term_num;
}jdentity2_t;


/**
 * @brief ���Ƽ��汾��offline�汾��ģ�ʹʵ�
 */
typedef struct JR_DICT_T{

	kword_model_t *twmodel;		  /**<  �ؼ��ʴʵ䣻      */
	xf_segdict_t *segdict;		  /**<  �ִʴʵ�      */

	jdentity_t *jd_list;		  /**<  ���е�jd�洢����      */
	u_int jd_num;		  /**<  jd ����      */

	jrword_t *info_term_weights;		  /**< ����jd��info�йؼ�����������      */
	u_int info_term_num;		  /**< info �ؼ���������Ԫ�ظ���       */

	jrword_t *title_term_weights;		  /**<  ����jd��title�йؼ��ʵ�����      */
	u_int title_term_num;		  /**<  title �ؼ���������Ԫ�ظ���      */
	JR_DICT_T():info_term_weights(NULL),jd_list(NULL),title_term_weights(NULL){}
}jrdict_t;


/**
 * @brief ����ṹ��
 */
typedef struct JR_RESULT_T{
	char key[JR_NAME_LENGTH];		  /**<  jd hash name      */
	u_int weight;		  /**<  jd���Ƽ�ʱ��Ӧ��Ȩ��      */
}jrresult_t;



/**
 * @brief offline �汾����ʱ����Ҫ�߳���ص�buffer
 */
typedef struct JR_OUT_T{
	xf_segout_t *segout;		  /**<  �ִ���Ҫ��buffer      */
	jrresult_t *results;		  /**< ����ṹ������       */
	u_int results_num;		  /**< ����ṹ���������󳤶�       */

	jrword_t info_term_weights[JR_MAX_KEYWORDS_NUM];		  /**<  ����ǰcv / jd ʱ��Ӧ��info �ؼ�������      */
	u_int info_term_num;
	
	jrword_t title_term_weights[JR_MAX_KEYWORDS_NUM];		  /**<  ����ǰcv / jd ʱ��Ӧ�� title �ؼ�������      */
	u_int title_term_num;

}jrout_t;




/**
 * @brief jr_create_out �����߳���ص�buffer
 *
 * @param max_jds_num  ���jd����; �����sphnix�У������дsphinx���ؼ���������������
 *
 * @return �߳���ص�bufferָ��
 */
jrout_t *jr_create_out(u_int max_jds_num = 1000000);

/**
 * @brief jr_destroy_out ���ٽṹ��
 *
 * @param pout
 */
void jr_destroy_out(jrout_t *& pout);


/**
 * @brief jr_load_model �Ӷ�����ģ����load jd��ģ��
 *
 * @param model_dir ģ��·����ַ
 *
 * @return �߳��޹ص�ȫ�ֱ���buffer
 */
jrdict_t *jr_load_model(const char *model_dir); 

/**
 * @brief jr_destroy_model �ͷ������Ǹ�ģ��
 *
 * @param pdict
 */
void jr_destroy_model(jrdict_t *&pdict);



int jr_load_inner_model(jrdict_t *pdict, const char *model_dir);

/**
 * @brief jr_build_model ����ģ��
 *
 * @param model_dir Ҫ��ŵ�ģ���ļ���
 * @param jd_file Ҫ��ģ�͵�jd����
 * @param jd_num jd�ĸ�����
 *
 * @return 
 */
int jr_build_model(const char *model_dir, const char *jd_file, u_int jd_num);


/**
 * @brief jr_calc_cv_jds  ����cvdata������jd�����ƶȲ�������洢��pout->results��
 *
 * @param pdict �߳��޹ر���
 * @param pout �߳���ر���
 * @param cvdata cv�����ݽṹ��
 *
 * @return 0�ɹ���-1ʧ��
 */
int jr_calc_cv_jds(jrdict_t *pdict, jrout_t *pout, jrdata_t &cvdata);

/**
 * @brief jr_calc_cv_jd ���㵥��cv jd�������
 * �ڵ��ñ�����ǰ��Ҫ���� jrdata_to_keywords(pdict, pout,
 * cvdata);����cvdata�е����ݼ����pout�� title_term_weights & info_term_weights;
 * @param pdict 
 * @param pentity ÿ��jd�ṹ��
 * @param pout 
 *
 * @return 
 */
u_int jr_calc_cv_jd(jrdict_t *pdict, jdentity_t *pentity, jrout_t *pout);
u_int jr_calc_cv_jd(jdentity2_t *pentity, jrout_t *pout);

/**
 * @brief jrdata_to_keywords ��jrbuf�е����ݣ���ȡ�ؼ��ʣ��ŵ�pout�У�
 *
 * @param pdict �μ�����ע�ͣ�
 * @param pout �μ�����ע�ͣ�
 * @param jrbuf �μ�����ע�ͣ�
 *
 * @return 
 */
int jrdata_to_keywords(jrdict_t *pdict, jrout_t *pout, jrdata_t &jrbuf);

/**
 * @brief jr_append_jrdata
 * ����python�������cv/jd�ṹ�����ݡ���������������ṹ�����ݵ�type��ֵ��info & weight copy
 * ��jrbuf��
 *
 * @param jrbuf �����洢ÿ��cv / jd ������
 * @param type �������ݵ�����
 * @param info �������ݵ�����
 * @param weight
 * �������ݵ�Ȩ����Ϣ�������û����������趨�ṹ�����ݵ�Ȩ�أ���ˣ�����û�����ĳ���ṹ������Ȩ�ر�����ֵ�������ô�һ�㣬Ĭ��Ϊ1��
 *
 * @return 
 */
int jr_append_jrdata(jrdata_t &jrbuf, jrdata_type_t type, const char *info, u_int weight);


/**
 * @brief jr_reset_jrdata 
 *
 * @param jrd
 *
 * @return 
 */
int jr_reset_jrdata(jrdata_t &jrd);

/**
 * @brief jr_reset_poutdata 
 *
 * @param pout
 *
 * @return 
 */
int jr_reset_poutdata(jrout_t *pout);


/**
 * @brief print_results 
 *
 * @param lastkey
 * @param results
 * @param results_num
 */
void print_results(const char *lastkey, jrresult_t *results, u_int results_num);



#endif  //__JOBRECMD_H_

/* vim: set ts=4 sw=4 sts=4 tw=100 noet: */
