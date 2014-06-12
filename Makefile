WORKROOT	= ./

ULIB=$(WORKROOT)/libs/
ULIBCMD=$(WORKROOT)/jobrmd/
CC	= g++ 

INCLUDES	=	-I./ \
				-I$(ULIBCMD)/include/ \
				-I$(ULIB)/segments/include \
				-I$(ULIB)/keywords/include \
				-I$(ULIB)/eigen/ 

LDFLAGS	=	-L./ \
			-L$(ULIBCMD)/lib/ -ljobrmd \
			-L$(ULIB)/keywords/lib -lkeyword \
			-L$(ULIB)/segments/lib -lsegments \
			-lcrypto -lm -lz -lpthread 

CFLAGS      = -g -DLINUX -DDEBUG_OFF -D_REENTRANT -Wall 

MakeTool= jrtest

#=========================================================================#

all : $(MakeTool) output

#---------------- MakeTool ---------------------

jrbuild: jrbuild.cpp
	$(CC) -o $@  $^  $(LDFLAGS) $(INCLUDES) $(CFLAGS)
jrtest: jrtest.cpp
	$(CC) -o $@  $^  $(LDFLAGS) $(INCLUDES) $(CFLAGS)
output : 
	rm -rf output;

clean :
	rm -rf $(MakeTool)
	rm -rf output
