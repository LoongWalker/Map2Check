/**
 * This module will check/analyze/validate all signed integer operations
 */

#include "Map2CheckFunctions.h"
#include "Map2CheckTypes.h"
#ifndef BinaryOperation_H
#define BinaryOperation_H

/**
 * @brief Checks ADD (on two integers) operations and adds cases where operation
 * would fail.
 * @param param1 First operand
 * @param param2 Second operand
 * @param line Line where operation occured
 * @param scope Scope where operation occured
 * @param function_name Name of the function which operation occured
 */
void map2check_binop_add(int param1, int param2, unsigned line, unsigned scope,
                         char* function_name);

void map2check_binop_add_uint(unsigned param1, unsigned param2, unsigned line,
                              unsigned scope, char* function_name);
/**
 * @brief Checks SUB (on two integers) operations and adds cases where operation
 * would fail.
 * @param param1 First operand
 * @param param2 Second operand
 * @param line Line where operation occured
 * @param scope Scope where operation occured
 * @param function_name Name of the function which operation occured
 * */
void map2check_binop_sub(int param1, int param2, unsigned line, unsigned scope,
                         char* function_name);

void map2check_binop_sub_uint(unsigned param1, unsigned param2, unsigned line,
                              unsigned scope, char* function_name);

/**
 * @brief Checks MUL (on two integers) operations and adds cases where operation
 * would fail.
 * @param param1 First operand
 * @param param2 Second operand
 * @param line Line where operation occured
 * @param scope Scope where operation occured
 * @param function_name Name of the function which operation occured
 * */
void map2check_binop_mul(int param1, int param2, unsigned line, unsigned scope,
                         char* function_name);

void map2check_binop_mul_uint(unsigned param1, unsigned param2, unsigned line,
                              unsigned scope, char* function_name);

/**
 * @brief Checks DIV (on two integers) operations and adds cases where operation
 * would fail.
 * @param param1 First operand
 * @param param2 Second operand
 * @param line Line where operation occured
 * @param scope Scope where operation occured
 * @param function_name Name of the function which operation occured
 * */
void map2check_binop_sdiv(int param1, int param2, unsigned line, unsigned scope,
                          char* function_name);

#endif