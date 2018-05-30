#!/bin/bash

RUNDIR=`pwd`
CLANG_PATH=$RUNDIR/dependencies/clang/bin

# Check if LLVM is already downloaded
# TODO: Check for distro before downloading
get_llvm()
{
	
	if [ ! -d clang ]; then	
		echo "Clang not found, downloading it"		
		curl http://releases.llvm.org/6.0.0/clang+llvm-6.0.0-x86_64-linux-gnu-ubuntu-16.04.tar.xz | tar -xJ
		mv clang+llvm-6.0.0-x86_64-linux-gnu-ubuntu-16.04 clang
  fi
}

# Fix for when user has LLVM in the system


# Check if AFL is already downloaded and build it using clang
get_afl()
{	
	if [ ! -d afl-2.52b ]; then	
		echo "AFL not found, downloading it"		
		curl http://lcamtuf.coredump.cx/afl/releases/afl-latest.tgz | tar -xz
		echo "Building AFL"
		cd afl-2.52b
		PATH="../clang/bin:$PATH" CC=clang CXX=clang++ make
		cd ..
  fi
}

map2check_get_deps() 
{
  cd $RUNDIR
  if [ ! -d dependencies ]; then	
		mkdir dependencies    
 	fi
  cd dependencies
   
	 get_llvm
	 get_afl
	 echo "Everything OK!"
	 cd -	
}

map2check_get_deps
