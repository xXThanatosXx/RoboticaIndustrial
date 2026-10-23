// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from arm_msgs:srv/AddTwoInts.idl
// generated code does not contain a copyright notice

#ifndef ARM_MSGS__SRV__DETAIL__ADD_TWO_INTS__STRUCT_H_
#define ARM_MSGS__SRV__DETAIL__ADD_TWO_INTS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in srv/AddTwoInts in the package arm_msgs.
typedef struct arm_msgs__srv__AddTwoInts_Request
{
  int64_t a;
  int64_t b;
} arm_msgs__srv__AddTwoInts_Request;

// Struct for a sequence of arm_msgs__srv__AddTwoInts_Request.
typedef struct arm_msgs__srv__AddTwoInts_Request__Sequence
{
  arm_msgs__srv__AddTwoInts_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arm_msgs__srv__AddTwoInts_Request__Sequence;


// Constants defined in the message

/// Struct defined in srv/AddTwoInts in the package arm_msgs.
typedef struct arm_msgs__srv__AddTwoInts_Response
{
  int64_t sum;
} arm_msgs__srv__AddTwoInts_Response;

// Struct for a sequence of arm_msgs__srv__AddTwoInts_Response.
typedef struct arm_msgs__srv__AddTwoInts_Response__Sequence
{
  arm_msgs__srv__AddTwoInts_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arm_msgs__srv__AddTwoInts_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ARM_MSGS__SRV__DETAIL__ADD_TWO_INTS__STRUCT_H_
