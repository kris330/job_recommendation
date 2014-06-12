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
 * 相关变量
 */
const u_int JR_STACK_SIZE = 512;	
const u_int JR_INFO_MAX_SIZE = 102400;
const u_int JRC_PAIR_MAX_NUM = 10;
const u_int JR_MAX_KEYWORDS_NUM = 10;
const u_int JR_NAME_LENGTH = 64;



/**
 * @brief 输入数据的格式；目前暂时定义为两种：职位或者简历的标题(_title) 和 其他内容信息
 */
typedef enum JRDATA_TYPE_T{
	_title=0,
	_info=1,
}jrdata_type_t;


/**
 * @brief 简历 职位 输入数据的结构体；
 */
typedef struct JR_DATA_T{
	char name[JR_NAME_LENGTH];		  /**<   jd cv 对应的文件名(hash值)     */
	char title[JR_STACK_SIZE];		  /**<   jd职位名 或者 cv求职意向名    */

	std::vector<std::pair<std::string, u_int > > info;		  /**<  jd cv 各种非title的结构化信息以及对应的权重     */

	std::vector<std::pair<std::string, u_int > > title_term_weights;
	std::vector<std::pair<std::string, u_int > > info_term_weights;

}jrdata_t;


/**
 * @brief 关键词信息； 
 */
typedef struct JR_WORD_T{
	uint64_t word_id;		  /**<  关键词ID      */
	u_int word_weight;		  /**<  关键词权重      */
}jrword_t;


/**
 * @brief 每个简历的结构体信息
 */
typedef struct JD_ENTITY_T{
	char jdname[JR_NAME_LENGTH];		  /**<  每个简历的hash id 字符串值      */

	u_int infot_begin;		  /**<  jd info关键词在pdict->info_term_weights中的起始位置      */
	u_int infot_len;  /**<  jd info关键词在pdict->info_term_weights中的长度值     */

	u_int titlet_begin;	  /**<  jd title 关键词在pdict->info_term_weights中的起始位置      */
	u_int titlet_len; /**<  jd title 关键词在pdict->info_term_weights中的长度值     */

}jdentity_t;




typedef struct JD_ENTITY_T2{
	char jdname[JR_NAME_LENGTH];		  /**< jd name  */
	jrword_t title_term_weights[JR_MAX_KEYWORDS_NUM+1];
	u_int title_term_num;
	jrword_t info_term_weights[JR_MAX_KEYWORDS_NUM+1];
	u_int info_term_num;
}jdentity2_t;


/**
 * @brief 本推荐版本中offline版本的模型词典
 */
typedef struct JR_DICT_T{

	kword_model_t *twmodel;		  /**<  关键词词典；      */
	xf_segdict_t *segdict;		  /**<  分词词典      */

	jdentity_t *jd_list;		  /**<  所有的jd存储在这      */
	u_int jd_num;		  /**<  jd 数量      */

	jrword_t *info_term_weights;		  /**< 所有jd的info中关键词向量在这      */
	u_int info_term_num;		  /**< info 关键词向量的元素个数       */

	jrword_t *title_term_weights;		  /**<  所有jd的title中关键词的向量      */
	u_int title_term_num;		  /**<  title 关键词向量的元素个数      */
	JR_DICT_T():info_term_weights(NULL),jd_list(NULL),title_term_weights(NULL){}
}jrdict_t;


/**
 * @brief 结果结构体
 */
typedef struct JR_RESULT_T{
	char key[JR_NAME_LENGTH];		  /**<  jd hash name      */
	u_int weight;		  /**<  jd被推荐时对应的权重      */
}jrresult_t;



/**
 * @brief offline 版本计算时所需要线程相关的buffer
 */
typedef struct JR_OUT_T{
	xf_segout_t *segout;		  /**<  分词需要的buffer      */
	jrresult_t *results;		  /**< 结果结构体数组       */
	u_int results_num;		  /**< 结果结构体数组的最大长度       */

	jrword_t info_term_weights[JR_MAX_KEYWORDS_NUM];		  /**<  处理当前cv / jd 时对应的info 关键词向量      */
	u_int info_term_num;
	
	jrword_t title_term_weights[JR_MAX_KEYWORDS_NUM];		  /**<  处理当前cv / jd 时对应的 title 关键词向量      */
	u_int title_term_num;

}jrout_t;




/**
 * @brief jr_create_out 创建线程相关的buffer
 *
 * @param max_jds_num  最大jd数量; 如果在sphnix中，这儿填写sphinx返回检索结果的最大数量
 *
 * @return 线程相关的buffer指针
 */
jrout_t *jr_create_out(u_int max_jds_num = 1000000);

/**
 * @brief jr_destroy_out 销毁结构体
 *
 * @param pout
 */
void jr_destroy_out(jrout_t *& pout);


/**
 * @brief jr_load_model 从二进制模型中load jd的模型
 *
 * @param model_dir 模型路径地址
 *
 * @return 线程无关的全局变量buffer
 */
jrdict_t *jr_load_model(const char *model_dir); 

/**
 * @brief jr_destroy_model 释放上面那个模型
 *
 * @param pdict
 */
void jr_destroy_model(jrdict_t *&pdict);



int jr_load_inner_model(jrdict_t *pdict, const char *model_dir);

/**
 * @brief jr_build_model 建立模型
 *
 * @param model_dir 要存放的模型文件夹
 * @param jd_file 要建模型的jd明文
 * @param jd_num jd的个数；
 *
 * @return 
 */
int jr_build_model(const char *model_dir, const char *jd_file, u_int jd_num);


/**
 * @brief jr_calc_cv_jds  计算cvdata与所有jd的相似度并将结果存储到pout->results中
 *
 * @param pdict 线程无关变量
 * @param pout 线程相关变量
 * @param cvdata cv的数据结构体
 *
 * @return 0成功，-1失败
 */
int jr_calc_cv_jds(jrdict_t *pdict, jrout_t *pout, jrdata_t &cvdata);

/**
 * @brief jr_calc_cv_jd 计算单个cv jd的相关性
 * 在调用本函数前需要调用 jrdata_to_keywords(pdict, pout,
 * cvdata);来将cvdata中的数据计算成pout中 title_term_weights & info_term_weights;
 * @param pdict 
 * @param pentity 每个jd结构体
 * @param pout 
 *
 * @return 
 */
u_int jr_calc_cv_jd(jrdict_t *pdict, jdentity_t *pentity, jrout_t *pout);
u_int jr_calc_cv_jd(jdentity2_t *pentity, jrout_t *pout);

/**
 * @brief jrdata_to_keywords 把jrbuf中的数据，提取关键词，放到pout中；
 *
 * @param pdict 参加其他注释；
 * @param pout 参见其他注释；
 * @param jrbuf 参见其他注释；
 *
 * @return 
 */
int jrdata_to_keywords(jrdict_t *pdict, jrout_t *pout, jrdata_t &jrbuf);

/**
 * @brief jr_append_jrdata
 * 读入python解析后的cv/jd结构化数据。本函数根据这个结构化数据的type的值将info & weight copy
 * 到jrbuf中
 *
 * @param jrbuf 用来存储每个cv / jd 的数据
 * @param type 该行数据的类型
 * @param info 该行数据的内容
 * @param weight
 * 该行数据的权重信息；由于用户可以自已设定结构化数据的权重，因此，如果用户想让某个结构体数据权重变大，这个值可以设置大一点，默认为1；
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
