# Attendance System Changes

## Overview
The attendance system has been enhanced to provide more flexibility in handling student attendance and associated charges.

## New Features

### 1. Enhanced Attendance Options

The system now supports three types of attendance:

#### **Present** (Student Attended)
- `isAbsent: false`
- `charge_money: true`
- **Effect**: Increments lesson count, deducts lesson cost from student's balance

#### **Absent - Excused** (Absent with Valid Reason, No Charge)
- `isAbsent: true`
- `charge_money: false`
- `reason: <explanation>`
- **Effect**: No lesson count change, no money deducted (e.g., sick leave, emergency)

#### **Absent - Unexcused** (Absent but Still Charged)
- `isAbsent: true`
- `charge_money: true`
- `reason: <explanation>`
- **Effect**: No lesson count change, but money is still deducted

### 2. Changeable Attendance

Attendance records can now be fully modified after creation. The system automatically:
- Adjusts lesson counts when changing between present/absent
- Refunds or charges money when changing the `charge_money` status
- Updates reasons and other details

## API Usage

### Recording Attendance

**Endpoint**: `POST /attendance/check`

**Example 1: Mark Student as Present**
```json
{
  "student_id": 1,
  "course_id": 5,
  "date": "2025-10-22",
  "isAbsent": false,
  "charge_money": true,
  "reason": ""
}
```

**Example 2: Mark Student as Absent - Excused (No Charge)**
```json
{
  "student_id": 1,
  "course_id": 5,
  "date": "2025-10-22",
  "isAbsent": true,
  "charge_money": false,
  "reason": "Medical emergency"
}
```

**Example 3: Mark Student as Absent - Unexcused (With Charge)**
```json
{
  "student_id": 1,
  "course_id": 5,
  "date": "2025-10-22",
  "isAbsent": true,
  "charge_money": true,
  "reason": "Did not show up"
}
```

### Updating Attendance

**Endpoint**: `PUT /attendance/student/{student_id}?date=YYYY-MM-DD&course_id={course_id}`

**Example 1: Change from Absent to Present**
```json
{
  "date": "2025-10-22",
  "course_id": 5,
  "isAbsent": false,
  "charge_money": true,
  "reason": ""
}
```

**Example 2: Change from Unexcused to Excused Absence**
```json
{
  "date": "2025-10-22",
  "course_id": 5,
  "isAbsent": true,
  "charge_money": false,
  "reason": "Doctor's note provided later"
}
```

**Example 3: Update Only the Reason**
```json
{
  "date": "2025-10-22",
  "course_id": 5,
  "reason": "Updated reason for absence"
}
```

### Getting Attendance Records

**Endpoint**: `GET /attendance/student/{student_id}`

Returns all attendance records for the student, including the new `charge_money` field.

## Data Model Changes

### AttendanceCheck Schema
```python
{
  "student_id": int,
  "course_id": int,
  "date": date,
  "isAbsent": bool,           # Default: false
  "reason": str (optional),   # Default: ""
  "charge_money": bool        # Default: true
}
```

### AttendanceUpdate Schema
```python
{
  "date": date,
  "course_id": int (optional),
  "isAbsent": bool (optional),
  "reason": str (optional),
  "charge_money": bool (optional)
}
```

### AttendanceRecord (in Student data)
```python
{
  "date": "YYYY-MM-DD",
  "course_id": int,
  "isAbsent": bool,
  "reason": str,
  "charge_money": bool
}
```

## Business Logic

### Financial Impact

The system calculates the lesson cost as:
```
lesson_cost = course.cost / course.lesson_per_month
```

**When `charge_money = true`**:
- Money is deducted from `student.total_money`
- If student is present (`isAbsent = false`), lesson count is also incremented

**When `charge_money = false`**:
- No money is deducted
- Lesson count is not affected

### Update Scenarios

When updating attendance, the system handles various scenarios:

1. **Changing charge status only**:
   - From charged to not charged → Refunds the lesson cost
   - From not charged to charged → Deducts the lesson cost

2. **Changing attendance status**:
   - From absent to present (both charged) → Increments lesson count
   - From present to absent (both charged) → Decrements lesson count

3. **Combined changes**:
   - The system first refunds the old status, then applies the new status

## Migration Notes

### Backward Compatibility

- Old attendance records without `charge_money` field default to `true` (money was charged)
- This maintains consistency with previous behavior where all attendance resulted in charges

### Recommended Migration Steps

1. All existing attendance records will automatically use `charge_money: true` as default
2. No database migration is required as the new field is stored in the JSON `attendance` column
3. Frontend applications should be updated to:
   - Display the charge status in attendance lists
   - Provide UI controls for selecting charge_money when recording attendance
   - Show appropriate indicators for excused vs unexcused absences

## Testing Recommendations

1. **Test Present Attendance**:
   - Verify lesson count increases
   - Verify money is deducted

2. **Test Excused Absence**:
   - Verify lesson count doesn't change
   - Verify money is NOT deducted

3. **Test Unexcused Absence**:
   - Verify lesson count doesn't change
   - Verify money IS deducted

4. **Test Attendance Updates**:
   - Change from present to absent and verify refund
   - Change from absent to present and verify charge
   - Change charge_money status and verify financial adjustment
   - Verify multiple updates don't cause incorrect calculations

## Implementation Files Modified

1. **`app/schemas/__init__.py`**: Added `charge_money` field to attendance schemas
2. **`app/models/__init__.py`**: Updated `add_attendance_record()` method with new logic
3. **`app/crud/student.py`**: Updated `add_attendance_record()` and `update_attendance_record()` functions
4. **`app/api/attendance.py`**: Updated API endpoints to handle new field
