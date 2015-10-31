#!/usr/bin/env python
# -*- coding: latin1 -*-

from __future__ import print_function

import sys
import os
import commands
import re


# From PycParser
import pycparser.c_parser
import pycparser.c_ast
from pycparser.c_ast import *
import pycparser.c_generator


# -------------------------------------------------
# Global Variables
# Portable cpp path for Windows and Linux/Unix
CPPPATH = '../map2check/utils/cpp.exe' if sys.platform == 'win32' else 'cpp'
ABS_PATH = os.path.dirname(__file__)
# -------------------------------------------------

class CheckPtrDecl(NodeVisitor):
    def __init__(self):
        self.linenum = 0
        self.check = False        

    def visit_PtrDecl(self, node):
        self.check = True 
        self.linenum = node.coord
        #print("---------", node.coord)  
        
        
class CheckArrayDecl(NodeVisitor):
    def __init__(self):
        self.linenum = 0
        self.check = False        

    def visit_ArrayDecl(self, node):
        self.check = True 
        self.linenum = node.coord
        #print("---------", node.coord)


class CheckTypeDef(NodeVisitor):
    def __init__(self):
        self.linenum = 0
        self.check = False        

    def visit_Typedef(self, node):
        self.check = False
        if self.checkIsTypeDefFromCode(node): 
#            print("Here")       
            ##if type(node.type) is TypeDecl:
            viar = CheckArrayDecl()
            viar.visit(node)
            viptr = CheckPtrDecl()
            viptr.visit(node)
            
            #print(self.getNumberOfLine(viar.linenum),"<>>>>",self.getNumberOfLine(viptr.linenum))
            if viar.check and viptr.check:
               if int(self.getNumberOfLine(viar.linenum)) == \
                  int(self.getNumberOfLine(viptr.linenum)):
                    #print(node.coord)
                    #print(viar.linenum,"<>>>>",viptr.linenum)
                    self.check = True
                
    @staticmethod
    def getNumberOfLine(nodecoord):
        #print(nodeVar)
        txt = str(nodecoord)
        matchNumLine = re.search(r'(.[^:]+)$', txt)
        if matchNumLine:
            onlyNumber = matchNumLine.group(1).replace(":","")
            return onlyNumber
            
    
    def checkIsTypeDefFromCode(self, node):
        """
        Identify the typedef node from AST related to C program, i.e.,
        exclude typedef from fake_libc_include/_fake_typedefs.h
        """
                
        if type(node) == Typedef:                
            matchTypeDef_Fake_typedefs = re.search(r'(fake_libc_include/_fake_typedefs.h)', str(node.coord))
            if not matchTypeDef_Fake_typedefs:
                #print(node.coord)
                return True
            else:
                return False
            


class IdentifyNotSupported(object):
    def __init__(self, _cfilepath):
        self.cfilepath = _cfilepath
        self.check = False


    def identify_structures_stop(self):

        path_cpp_args = os.path.join(os.path.dirname(__file__), "../map2check/utils/fake_libc_include")        
        ast = pycparser.parse_file(self.cfilepath, use_cpp=True, cpp_path=CPPPATH, cpp_args=r'-I'+path_cpp_args)
        #ast.show()        
        #sys.exit()
        
        vi = CheckTypeDef()
        # Not supported pointer with arrays, eg:
        # typedef void *item_t[2];        
        for index in range(0,len(ast.ext)):                                     
            vi.visit(ast.ext[index])
            if vi.check:                
                self.check = vi.check
                #break
                return self.check
            else:
                self.check = False
                
        

        

