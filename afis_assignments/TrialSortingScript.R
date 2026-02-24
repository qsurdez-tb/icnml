#Import real data txt file into R
ICNMLset <- read.csv("~/R/Close non-match/afis_assignments/ICNMLset.txt", sep=";", stringsAsFactors=FALSE, header = FALSE)
UUID <- ICNMLset[[1]] 
donor_number<- ICNMLset[[2]]  
printregion <-ICNMLset[[3]] 
count <- ICNMLset [[4]]  
submitternumber <-ICNMLset[[5]]
ICNMLlist <- list(UUID, donor_number, printregion, count, submitternumber)
names(ICNMLlist) <- c("UUID", "Donor number", "print region", "count", "submitter number")


#Import dummy list of labs by name and convert to AFIS compatible
listoflabs <- read.table("~/R/Close non-match/afis_assignments/listoflabs.txt", quote="\"", comment.char="")
listoflabs <- as.vector(unlist(listoflabs))
for (i in 1:length(listoflabs)){
    if (listoflabs[i] == "Houston") {
    listoflabs[i] <- "submitter_1"}
    else if (listoflabs[i] == "Sweden") 
    listoflabs[i] <- "submitter_2"
    else if (listoflabs[i] == "Arizona") {
    listoflabs[i] <- "submitter_3"
  }  else if (listoflabs[i] == "Romania") {
    listoflabs[i] <- "submitter_4"
  }  else if (listoflabs[i] == "LA") {
    listoflabs[i] <- "submitter_5"
  }  else if (listoflabs[i] == "Israel") {
    listoflabs[i] <- "submitter_6"
  }  else if (listoflabs[i] == "Quebec") {
    listoflabs[i] <- "submitter_7"
  }  else if (listoflabs[i] == "Minnesota") {
    listoflabs[i] <- "submitter_8"
  }  else if (listoflabs[i] == "UK2") {
    listoflabs[i] <- "submitter_9"
  }  else if (listoflabs[i] == "ScotlandYard") {
    listoflabs[i] <- "submitter_10"
  }
}
 

 
library(readxl)
dummydata2 <- read_excel("R/Close non-match/dummydata2.xlsx")
dummydataframe <- unlist(dummydata2)
dummydataframe <- matrix(dummydataframe, ncol = 5, byrow = FALSE)
colnames(dummydataframe) <- c("data name", "Donor lab", "Data type", "Donor number", "Receiving lab")

read.csv("C:\\Users\\lta\\Documents\\R\\Close non-match\\listoflabs.csv", header = TRUE)
labsdonating <- read_excel("listoflabs.xlsx")
labsdonating <-(unlist(labsdonating))

#removing the donating lab from the list of labs to sample from 
for (i in ICNMLlist$`submitter number`) {
    if (is.element(listoflabs, i)){
    dontinclude <- ICNMLlist$`submitter number`[i]
    ICNMLlist$`set to sample from`[i] <- listoflabs[!is.element(listoflabs,dontinclude)] 
    ICNMLlist[['recipient']][i] <- sample(ICNMLlist[['set to sample from']][i], 1)}}
    #how to determine how to print these results out to a new table?
  
  
    ICNMLlist[['submitter number']][i] != listoflabs[i]{
    dontinclude <- listoflabs[i]
    samplethis <- listoflabs[!is.element(listoflabs,listoflabs[i])]
    receivinglab.i <- sample(samplethis, i)
    samplethis <- vsetdiff(listoflabs, receivinglab.i)
  }}

#List of labs donating data files, number of elements = number of files donating

library(readxl)
labsdonatingandreceiving <- read_excel("R/Close non-match/listoflabs.xlsx", 
                                       sheet = "Sheet2", col_names = FALSE)
labsdonating <- as.vector(unlist(labsdonatingandreceiving))

num.Houston.left <- length(which(labsdonating == "Houston"))
num.Sweden.left <- length(which(labsdonating == "Sweden"))
num.Arizona.left <- length(which(labsdonating == "Arizona"))
num.LA.left <- length(which(labsdonating == "LA"))
num.Israel.left <- length(which(labsdonating == "Israel"))
num.Quebec.left <- length(which(labsdonating == "Quebec"))
num.Minnesota.left <- length(which(labsdonating == "Minnesota"))
num.Romania.left <- length(which(labsdonating == "Romania"))
num.UK2.left <- length(which(labsdonating == "UK2"))
num.ScotlandYard.left <- length(which(labsdonating == "ScotlandYard"))


#lab exclusions
notHouston <- labsdonating[!is.element(, "Houston")]
notSweden <- labsdonating[!is.element(labsdonating, "Sweden")]
notArizona <- labsdonating[!is.element(labsdonating, "Arizona")]
notLA <- labsdonating[!is.element(labsdonating, "LA")]
notIsrael <- labsdonating[!is.element(labsdonating, "Israel")]
notQuebec <-labsdonating[!is.element(labsdonating, "Quebec")]
              
#function to filter available choices of lab based only on Donating lab

filterdonorlab <- function(Donorlab) {
  if(Donorlab == "Sweden") {output <- notSweden}
  else if(Donorlab == "Houston") {output <- notHouston}
  else if(Donorlab == "Arizona") {output <- notArizona}
  else if(Donorlab == "LA") {output <- notLA}
  else if(Donorlab == "Israel") {output <- notIsrael}
  else if(Donorlab == "Quebec") {output <- notQuebec}
  else {output <- labsdonating}
}

filterdonorlab(dummydataframe[2,2])

n <- 1

slab.i <-sample(labchoices[[i]],1)

for(column.i in 1:nrow(dummydataframe)) {
  Donorlab.i <- dummydataframe[column.i]
}

#evaluate elements dummydataframe[[2]
for (y in dummydataframe[1,]){
  if ("Sweden" %in% dummydataframe[,1]) {
   sample(notSweden,1)
}}
    

for (x in 1:dummydataframe[x,1]){
  if ("Sweden" %in% dummydataframe[,1]){
    abc = sample(labsdonatingdf[labsdonatingdf!="Sweden"],1)
  }
  dummydataframe[x,5] = abc
}
s
#possibly a way to continually edit the dummydataframe with the lab the data is going to by using MUTATE function
# mutate(data, x4 = some result) where x4 is the name of the additional column? ==


# Can sort data based on the previous by asking if the donorvect variable contains a certain number 
# apply(dataframe, 1 (for row) or 2 (for column), function, arguments for function)

apply(df, 1, filterdonorlab)

#added comment

