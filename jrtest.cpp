/***************************************************************************
 * 
 * $Id$ 
 * 
 **************************************************************************/



/**
 * jrtest.cpp ~ 2014/03/15 21:52:54
 * @version $Revision$ 
 * @description 
 *  
 **/
#include "jobrecmd.h"


void print_pout(jrdata_t &jrbuf){
	printf("Keywords for title:\n");
	for(u_int i =0 ; i< jrbuf.title_term_weights.size(); i++){
		printf("%s[%u]\n",jrbuf.title_term_weights[i].first.c_str(), jrbuf.title_term_weights[i].second);
	}
	printf("Keywords for info:\n");
	for(u_int i = 0 ; i < jrbuf.info_term_weights.size(); i++){
		printf("%s[%u]\n",jrbuf.info_term_weights[i].first.c_str(), jrbuf.info_term_weights[i].second);
	}
}


int main(int argc, char **argv){
	if(argc != 2){
		fprintf(stderr, "Usage: %s model\n", argv[0]);
		return -1;
	}
	jrout_t  *pout = jr_create_out();
	jrdict_t *pdict = new jrdict_t();
	jr_load_inner_model(pdict, argv[1]);
	if(pout == NULL || pdict == NULL){
		fprintf(stderr, "pout or pdict is NULL\n");
		return -1;
	}

	char line[10240] = {};
	char key[JR_NAME_LENGTH]={};
	char lastkey[JR_NAME_LENGTH] = {};

	u_int type=0;
	char info[10240] = {};
	u_int line_weight_rate = 0;

	jrdata_t jrbuf;
	while(fgets(line,10239, stdin)){
		int len = strlen(line);
		while(line[len - 1] == '\r' || line[len-1] == '\n'){
			line[--len] = 0;
		}
		/**<  line_weight_rate 意图是为了人工调整jd cv 不同字段的重要性     */
		if(sscanf(line,"%[^\t]\t%u\t%[^\t]\t%u",key,&type,info,&line_weight_rate) != 4){
			fprintf(stderr, "Line [%s] format error!\n", line);
			continue;
		}
		if(strcmp(lastkey,key) == 0){
			jr_append_jrdata(jrbuf, (jrdata_type_t)type, info, line_weight_rate);
		}else{
			if(strlen(lastkey)>10){
				jrdata_to_keywords(pdict, pout, jrbuf);
				print_pout(jrbuf);
			}
			jr_reset_jrdata(jrbuf);
			jr_reset_poutdata(pout);
			sprintf(lastkey,"%s",key);
			snprintf(jrbuf.name, JR_NAME_LENGTH-1, "%s", key);
			jr_append_jrdata(jrbuf, (jrdata_type_t)type,info,line_weight_rate);
		}
	}
	jrdata_to_keywords(pdict, pout, jrbuf);
	print_pout(jrbuf);
	jr_destroy_model(pdict);
	return 0;
}








/* vim: set ts=4 sw=4 sts=4 tw=100 noet: */
