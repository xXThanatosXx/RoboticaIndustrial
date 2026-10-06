// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from arm_msgs:action/Fibonacci.idl
// generated code does not contain a copyright notice

#ifndef ARM_MSGS__ACTION__DETAIL__FIBONACCI__STRUCT_H_
#define ARM_MSGS__ACTION__DETAIL__FIBONACCI__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in action/Fibonacci in the package arm_msgs.
typedef struct arm_msgs__action__Fibonacci_Goal
{
  int32_t order;
} arm_msgs__action__Fibonacci_Goal;

// Struct for a sequence of arm_msgs__action__Fibonacci_Goal.
typedef struct arm_msgs__action__Fibonacci_Goal__Sequence
{
  arm_msgs__action__Fibonacci_Goal * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arm_msgs__action__Fibonacci_Goal__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'sequence'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in action/Fibonacci in the package arm_msgs.
typedef struct arm_msgs__action__Fibonacci_Result
{
  rosidl_runtime_c__int32__Sequence sequence;
} arm_msgs__action__Fibonacci_Result;

// Struct for a sequence of arm_msgs__action__Fibonacci_Result.
typedef struct arm_msgs__action__Fibonacci_Result__Sequence
{
  arm_msgs__action__Fibonacci_Result * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arm_msgs__action__Fibonacci_Result__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'partial_sequence'
// already included above
// #include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in action/Fibonacci in the package arm_msgs.
typedef struct arm_msgs__action__Fibonacci_Feedback
{
  rosidl_runtime_c__int32__Sequence partial_sequence;
} arm_msgs__action__Fibonacci_Feedback;

// Struct for a sequence of arm_msgs__action__Fibonacci_Feedback.
typedef struct arm_msgs__action__Fibonacci_Feedback__Sequence
{
  arm_msgs__action__Fibonacci_Feedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arm_msgs__action__Fibonacci_Feedback__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'goal'
#include "arm_msgs/action/detail/fibonacci__struct.h"

/// Struct defined in action/Fibonacci in the package arm_msgs.
typedef struct arm_msgs__action__Fibonacci_SendGoal_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
  arm_msgs__action__Fibonacci_Goal goal;
} arm_msgs__action__Fibonacci_SendGoal_Request;

// Struct for a sequence of arm_msgs__action__Fibonacci_SendGoal_Request.
typedef struct arm_msgs__action__Fibonacci_SendGoal_Request__Sequence
{
  arm_msgs__action__Fibonacci_SendGoal_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arm_msgs__action__Fibonacci_SendGoal_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in action/Fibonacci in the package arm_msgs.
typedef struct arm_msgs__action__Fibonacci_SendGoal_Response
{
  bool accepted;
  builtin_interfaces__msg__Time stamp;
} arm_msgs__action__Fibonacci_SendGoal_Response;

// Struct for a sequence of arm_msgs__action__Fibonacci_SendGoal_Response.
typedef struct arm_msgs__action__Fibonacci_SendGoal_Response__Sequence
{
  arm_msgs__action__Fibonacci_SendGoal_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arm_msgs__action__Fibonacci_SendGoal_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"

/// Struct defined in action/Fibonacci in the package arm_msgs.
typedef struct arm_msgs__action__Fibonacci_GetResult_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
} arm_msgs__action__Fibonacci_GetResult_Request;

// Struct for a sequence of arm_msgs__action__Fibonacci_GetResult_Request.
typedef struct arm_msgs__action__Fibonacci_GetResult_Request__Sequence
{
  arm_msgs__action__Fibonacci_GetResult_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arm_msgs__action__Fibonacci_GetResult_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'result'
// already included above
// #include "arm_msgs/action/detail/fibonacci__struct.h"

/// Struct defined in action/Fibonacci in the package arm_msgs.
typedef struct arm_msgs__action__Fibonacci_GetResult_Response
{
  int8_t status;
  arm_msgs__action__Fibonacci_Result result;
} arm_msgs__action__Fibonacci_GetResult_Response;

// Struct for a sequence of arm_msgs__action__Fibonacci_GetResult_Response.
typedef struct arm_msgs__action__Fibonacci_GetResult_Response__Sequence
{
  arm_msgs__action__Fibonacci_GetResult_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arm_msgs__action__Fibonacci_GetResult_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'feedback'
// already included above
// #include "arm_msgs/action/detail/fibonacci__struct.h"

/// Struct defined in action/Fibonacci in the package arm_msgs.
typedef struct arm_msgs__action__Fibonacci_FeedbackMessage
{
  unique_identifier_msgs__msg__UUID goal_id;
  arm_msgs__action__Fibonacci_Feedback feedback;
} arm_msgs__action__Fibonacci_FeedbackMessage;

// Struct for a sequence of arm_msgs__action__Fibonacci_FeedbackMessage.
typedef struct arm_msgs__action__Fibonacci_FeedbackMessage__Sequence
{
  arm_msgs__action__Fibonacci_FeedbackMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arm_msgs__action__Fibonacci_FeedbackMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ARM_MSGS__ACTION__DETAIL__FIBONACCI__STRUCT_H_
