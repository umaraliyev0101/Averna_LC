# Student Search and Pagination Fixes

## Issues Fixed

### 1. **Only First 100 Students Appearing**
   - **Problem**: The default limit was set to 100 students
   - **Solution**: Increased default limit to 1000 students (configurable up to 10,000)

### 2. **Search Not Working**
   - **Problem**: The API endpoint accepted search parameters (`name`, `surname`, `course_id`) but completely ignored them
   - **Solution**: Implemented proper search functionality using the existing `search_students()` CRUD function

## Changes Made

### File: `app/api/students.py`

#### GET /students/ endpoint
- **Increased default limit**: Changed from `100` to `1000` (max `10,000`)
- **Implemented search functionality**: Now properly uses `name`, `surname`, and `course_id` parameters
- **Smart filtering**: When search parameters are provided, the `search_students()` function is called instead of `get_students()`
- **Teacher filtering**: For teachers, search results are filtered to only show students in their assigned courses

#### GET /students/archived/ endpoint  
- **Increased default limit**: Changed from `100` to `1000` (max `10,000`)

### File: `app/crud/student.py`

Updated default limits for all student query functions:
- `get_students()`: 1000 → 10,000
- `search_students()`: 1000 → 10,000
- `get_students_by_course_ids()`: 1000 → 10,000
- `get_archived_students()`: 1000 → 10,000

## API Usage

### Get All Students (with pagination)
```http
GET /students/?skip=0&limit=1000
```

### Search by Name
```http
GET /students/?name=John
```
Returns all students whose name contains "John" (case-insensitive)

### Search by Surname
```http
GET /students/?surname=Smith
```
Returns all students whose surname contains "Smith" (case-insensitive)

### Search by Course
```http
GET /students/?course_id=5
```
Returns all students enrolled in course with ID 5

### Combined Search
```http
GET /students/?name=John&surname=Smith&course_id=5
```
Returns students matching all criteria

### Pagination with Search
```http
GET /students/?name=John&skip=0&limit=50
```
Search for "John" and return first 50 results

## Search Behavior

### For Admin and Superadmin:
- Can search across **all students**
- Search is case-insensitive
- Name and surname use partial matching (substring search)
- Multiple filters are combined with AND logic

### For Teachers:
- Can only search **students in their assigned courses**
- Search filters are applied first, then results are filtered by teacher's courses
- Same search capabilities as admins, but restricted to their scope

## Performance Considerations

- Default limit increased to 1000 to show more students by default
- Maximum limit is 10,000 to prevent excessive database load
- Search uses database indexes on `name`, `surname`, and joins for courses
- Pagination parameters (`skip` and `limit`) should be used for large result sets

## Examples

### Example 1: Get first 1000 students
```http
GET /students/
```

### Example 2: Get next 1000 students (pagination)
```http
GET /students/?skip=1000&limit=1000
```

### Example 3: Search for students named "Maria"
```http
GET /students/?name=Maria
```

### Example 4: Find all students in course 3
```http
GET /students/?course_id=3
```

### Example 5: Find "Maria" in course 3
```http
GET /students/?name=Maria&course_id=3
```

## Testing Recommendations

1. **Test pagination**: Verify that students beyond the first 100 now appear
2. **Test name search**: Search for partial names (e.g., "Mar" should find "Maria", "Marcus", "Margarita")
3. **Test surname search**: Search for partial surnames
4. **Test course filter**: Verify only students in specified course appear
5. **Test combined filters**: Use multiple search parameters together
6. **Test teacher restrictions**: Verify teachers only see students in their assigned courses
7. **Test case-insensitivity**: Search with different cases (e.g., "maria", "MARIA", "Maria")

## Backward Compatibility

- All changes are backward compatible
- Default behavior without parameters remains the same, just returns more students (1000 instead of 100)
- Existing API calls will continue to work
- No database schema changes required
