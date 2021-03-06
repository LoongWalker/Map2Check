#pragma once

#include <llvm/Analysis/LoopInfo.h>
#include <llvm/IR/Function.h>
#include <llvm/IR/IRBuilder.h>
#include <llvm/Pass.h>
#include <llvm/Support/raw_ostream.h>

#include <llvm/ADT/Statistic.h>
#include <llvm/Analysis/LoopInfo.h>
#include <llvm/Analysis/LoopPass.h>
#include <llvm/IR/InstIterator.h>
#include <llvm/IR/Instructions.h>

#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include <memory>

#include "../../frontend/utils/tools.hpp"
#include "DebugInfo.hpp"
#include "LibraryFunctions.hpp"

using namespace llvm;
namespace Tools = Map2Check;

struct LoopPredAssumePass : public LoopPass {
  static char ID;
  LoopPredAssumePass() : LoopPass(ID) {}

  virtual bool runOnLoop(Loop* L, LPPassManager& LPM);
  void getConditionInLoop(Loop* L);

 private:
  LLVMContext* Ctx;
  Constant* map2check_assume = NULL;
};
