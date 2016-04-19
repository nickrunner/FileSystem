#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#include <pwd.h>
#include <grp.h>
#include <time.h>
#include <locale.h>
#include <langinfo.h>
#include <stdio.h>
#include <stdint.h>

char const * sperm(__mode_t mode) {
    static char local_buff[16] = {0};
    int i = 0;
    // user permissions
    if ((mode & S_IRUSR) == S_IRUSR) local_buff[i] = 'r';
    else local_buff[i] = '-';
    i++;
    if ((mode & S_IWUSR) == S_IWUSR) local_buff[i] = 'w';
    else local_buff[i] = '-';
    i++;
    if ((mode & S_IXUSR) == S_IXUSR) local_buff[i] = 'x';
    else local_buff[i] = '-';
    i++;
    // group permissions
    if ((mode & S_IRGRP) == S_IRGRP) local_buff[i] = 'r';
    else local_buff[i] = '-';
    i++;
    if ((mode & S_IWGRP) == S_IWGRP) local_buff[i] = 'w';
    else local_buff[i] = '-';
    i++;
    if ((mode & S_IXGRP) == S_IXGRP) local_buff[i] = 'x';
    else local_buff[i] = '-';
    i++;
    // other permissions
    if ((mode & S_IROTH) == S_IROTH) local_buff[i] = 'r';
    else local_buff[i] = '-';
    i++;
    if ((mode & S_IWOTH) == S_IWOTH) local_buff[i] = 'w';
    else local_buff[i] = '-';
    i++;
    if ((mode & S_IXOTH) == S_IXOTH) local_buff[i] = 'x';
    else local_buff[i] = '-';
    return local_buff;
}

int main(int argc, char *argv[])
{
    DIR *dirPtr;

    struct dirent 	*entryPtr;
    struct stat 	statBuf;
    struct passwd 	*pwd;
    struct group 	*grp;
    struct tm		*tm;
    struct ino_t	*ino;
    struct dev_t	*dev;
    char			datestring[256];


    dirPtr = opendir(".");

    while ((entryPtr = readdir(dirPtr))){

    	//Fill stat buffer
    	if(stat(entryPtr->d_name, &statBuf) < 0){
    		continue;
    	}


    	//ls -l (show long listing)
    	if(strcmp(argv[1], "-l") == 0){

    		
    		//Print out type, permissions
    		printf("%10.10s", sperm(statBuf.st_mode));

    		//Print number of links
    		printf("%4d", statBuf.st_nlink);

    		//Print owner's name
    		if((pwd = getpwuid(statBuf.st_uid)) != NULL){
    			printf(" %-8.8s", pwd->pw_name);
    		}
    		else{
        		printf(" %-8d", statBuf.st_uid);
    		}
    		

    		/* Print out group name if it is found using getgrgid(). */
   			 if ((grp = getgrgid(statBuf.st_gid)) != NULL){
        		printf(" %-3.8s", grp->gr_name);
        	}
   			 else{
        		printf(" %-8d", statBuf.st_gid);
        	}

        	 /* Print size of file. */
    		printf(" %4jd", (intmax_t)statBuf.st_size);

    		tm = localtime(&statBuf.st_mtime);

    		/* Get localized date string. */
    		strftime(datestring, sizeof(datestring), nl_langinfo(D_T_FMT), tm);

    		printf(" %s %s", datestring, entryPtr->d_name);
    	}

    	//ls -i (Show inode #)
    	if(strcmp(argv[1], "-i") == 0){
    		//dev = statBuf.st_rdev;
    		printf("%u  ", statBuf.st_ino);
    		printf("%-20s", entryPtr->d_name);
    	}
    	printf("\n");

