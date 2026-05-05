-- ============================================
-- 1. USERS & AUTHENTICATION
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL DEFAULT '',
    last_login TIMESTAMP NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'faculty', 'department_head')),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 2. DEPARTMENTS
-- ============================================

CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    head_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 3. FACULTY
-- ============================================

CREATE TABLE IF NOT EXISTS faculty (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    specialization TEXT,
    max_teaching_load INTEGER DEFAULT 24,
    max_sections INTEGER DEFAULT 6,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'on_leave')),
    phone VARCHAR(20),
    office_location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 4. PROGRAMS
-- ============================================

CREATE TABLE IF NOT EXISTS programs (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    total_years INTEGER DEFAULT 4,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 5. SUBJECTS
-- ============================================

CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    units INTEGER NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('lecture', 'lab', 'lecture-lab')),
    hours_per_week INTEGER DEFAULT 3,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    year_level INTEGER NOT NULL CHECK (year_level BETWEEN 1 AND 4),
    semester INTEGER NOT NULL CHECK (semester IN (1, 2)),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 6. PREREQUISITES
-- ============================================

CREATE TABLE IF NOT EXISTS prerequisites (
    id SERIAL PRIMARY KEY,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    prerequisite_subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subject_id, prerequisite_subject_id)
);

-- ============================================
-- 7. ACADEMIC YEARS
-- ============================================

CREATE TABLE IF NOT EXISTS academic_years (
    id SERIAL PRIMARY KEY,
    year_code VARCHAR(20) UNIQUE NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 8. SEMESTERS
-- ============================================

CREATE TABLE IF NOT EXISTS semesters (
    id SERIAL PRIMARY KEY,
    academic_year_id INTEGER REFERENCES academic_years(id) ON DELETE CASCADE,
    semester_number INTEGER NOT NULL CHECK (semester_number IN (1, 2)),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(academic_year_id, semester_number)
);

-- ============================================
-- 9. SECTIONS
-- ============================================

CREATE TABLE IF NOT EXISTS sections (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
    year_level INTEGER NOT NULL CHECK (year_level BETWEEN 1 AND 4),
    section_name VARCHAR(10) NOT NULL,
    student_count INTEGER DEFAULT 0,
    max_capacity INTEGER DEFAULT 50,
    semester_id INTEGER REFERENCES semesters(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 10. CURRICULUM (Program-Year-Semester-Subject mapping)
-- ============================================

CREATE TABLE IF NOT EXISTS curriculum (
    id SERIAL PRIMARY KEY,
    program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    year_level INTEGER NOT NULL CHECK (year_level BETWEEN 1 AND 4),
    semester INTEGER NOT NULL CHECK (semester IN (1, 2)),
    is_required BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(program_id, subject_id, year_level, semester)
);

-- ============================================
-- 11. ROOMS
-- ============================================

CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    building VARCHAR(100),
    floor INTEGER,
    capacity INTEGER DEFAULT 30,
    type VARCHAR(20) CHECK (type IN ('classroom', 'laboratory', 'lecture_hall', 'gym')),
    facilities TEXT,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 12. TIME SLOTS
-- ============================================

CREATE TABLE IF NOT EXISTS time_slots (
    id SERIAL PRIMARY KEY,
    day_of_week VARCHAR(10) NOT NULL CHECK (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(day_of_week, start_time, end_time)
);

-- ============================================
-- 13. SCHEDULES (Main schedule table)
-- ============================================

CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY,
    faculty_id INTEGER REFERENCES faculty(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
    room_id INTEGER REFERENCES rooms(id) ON DELETE SET NULL,
    time_slot_id INTEGER REFERENCES time_slots(id) ON DELETE CASCADE,
    semester_id INTEGER REFERENCES semesters(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================
-- 14. TEACHING LOADS (Calculated/cached data)
-- ============================================

CREATE TABLE IF NOT EXISTS teaching_loads (
    id SERIAL PRIMARY KEY,
    faculty_id INTEGER REFERENCES faculty(id) ON DELETE CASCADE,
    semester_id INTEGER REFERENCES semesters(id) ON DELETE CASCADE,
    total_units INTEGER DEFAULT 0,
    total_hours INTEGER DEFAULT 0,
    total_sections INTEGER DEFAULT 0,
    status VARCHAR(20) CHECK (status IN ('underload', 'normal', 'overload')),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(faculty_id, semester_id)
);

-- ============================================
-- 15. SCHEDULE PATTERNS (for MWF, TTH patterns)
-- ============================================

CREATE TABLE IF NOT EXISTS schedule_patterns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    days VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 16. CONFLICTS (Log scheduling conflicts)
-- ============================================

CREATE TABLE IF NOT EXISTS conflicts (
    id SERIAL PRIMARY KEY,
    conflict_type VARCHAR(50) NOT NULL,
    schedule_id_1 INTEGER REFERENCES schedules(id) ON DELETE CASCADE,
    schedule_id_2 INTEGER REFERENCES schedules(id) ON DELETE CASCADE,
    description TEXT,
    status VARCHAR(20) DEFAULT 'unresolved' CHECK (status IN ('unresolved', 'resolved', 'ignored')),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolved_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================
-- 17. NOTIFICATIONS
-- ============================================

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(20) CHECK (type IN ('info', 'warning', 'error', 'success')),
    is_read BOOLEAN DEFAULT FALSE,
    link VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 18. AUDIT LOGS
-- ============================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 19. SYSTEM SETTINGS
-- ============================================

CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    data_type VARCHAR(20) CHECK (data_type IN ('string', 'integer', 'boolean', 'json')),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================
-- 20. HOLIDAYS
-- ============================================

CREATE TABLE IF NOT EXISTS holidays (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    type VARCHAR(20) CHECK (type IN ('regular', 'special', 'university')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 21. FACULTY AVAILABILITY
-- ============================================

CREATE TABLE IF NOT EXISTS faculty_availability (
    id SERIAL PRIMARY KEY,
    faculty_id INTEGER REFERENCES faculty(id) ON DELETE CASCADE,
    day_of_week VARCHAR(10) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(faculty_id, day_of_week, start_time)
);

-- ============================================
-- 22. SCHEDULE REQUESTS (for faculty to request changes)
-- ============================================

CREATE TABLE IF NOT EXISTS schedule_requests (
    id SERIAL PRIMARY KEY,
    faculty_id INTEGER REFERENCES faculty(id) ON DELETE CASCADE,
    schedule_id INTEGER REFERENCES schedules(id) ON DELETE CASCADE,
    request_type VARCHAR(20) CHECK (request_type IN ('change_time', 'change_room', 'swap', 'cancel')),
    reason TEXT NOT NULL,
    requested_changes JSONB,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES for Performance Optimization
-- ============================================

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

CREATE INDEX IF NOT EXISTS idx_faculty_user_id ON faculty(user_id);
CREATE INDEX IF NOT EXISTS idx_faculty_department_id ON faculty(department_id);
CREATE INDEX IF NOT EXISTS idx_faculty_status ON faculty(status);

CREATE INDEX IF NOT EXISTS idx_subjects_code ON subjects(code);
CREATE INDEX IF NOT EXISTS idx_subjects_department_id ON subjects(department_id);
CREATE INDEX IF NOT EXISTS idx_subjects_year_semester ON subjects(year_level, semester);

CREATE INDEX IF NOT EXISTS idx_schedules_faculty_id ON schedules(faculty_id);
CREATE INDEX IF NOT EXISTS idx_schedules_subject_id ON schedules(subject_id);
CREATE INDEX IF NOT EXISTS idx_schedules_section_id ON schedules(section_id);
CREATE INDEX IF NOT EXISTS idx_schedules_room_id ON schedules(room_id);
CREATE INDEX IF NOT EXISTS idx_schedules_semester_id ON schedules(semester_id);
CREATE INDEX IF NOT EXISTS idx_schedules_time_slot_id ON schedules(time_slot_id);

CREATE INDEX IF NOT EXISTS idx_sections_program_id ON sections(program_id);
CREATE INDEX IF NOT EXISTS idx_sections_semester_id ON sections(semester_id);
CREATE INDEX IF NOT EXISTS idx_sections_year_level ON sections(year_level);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_table_name ON audit_logs(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- ============================================
-- TRIGGERS for automated timestamp updates
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER IF NOT EXISTS update_users_updated_at BEFORE UPDATE ON users

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON departments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_faculty_updated_at BEFORE UPDATE ON faculty
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON programs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subjects_updated_at BEFORE UPDATE ON subjects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sections_updated_at BEFORE UPDATE ON sections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rooms_updated_at BEFORE UPDATE ON rooms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_schedules_updated_at BEFORE UPDATE ON schedules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- INITIAL DATA (Sample/Seed Data)
-- ============================================

-- Insert default admin user only if not exists
INSERT INTO users (username, email, password, first_name, last_name, role, is_staff, is_superuser)
VALUES ('admin', 'admin@chmsu.edu.ph', '', 'Admin', 'User', 'admin', TRUE, TRUE)
ON CONFLICT (username) DO NOTHING;

-- Insert Information Systems department only if not exists
INSERT INTO departments (code, name, description)
VALUES ('IS', 'Information Systems', 'Department of Information Systems')
ON CONFLICT (code) DO NOTHING;

-- Insert BSIS Program only if not exists
INSERT INTO programs (code, name, description, department_id)
VALUES ('BSIS', 'Bachelor of Science in Information Systems', 'BS Information Systems Program', 1)
ON CONFLICT (code) DO NOTHING;

-- Insert default schedule patterns only if not exists
INSERT INTO schedule_patterns (name, description, days) VALUES
('MWF', 'Monday-Wednesday-Friday', 'Monday,Wednesday,Friday'),
('TTH', 'Tuesday-Thursday', 'Tuesday,Thursday'),
('MW', 'Monday-Wednesday', 'Monday,Wednesday'),
('TH', 'Tuesday-Thursday', 'Tuesday,Thursday'),
('F', 'Friday Only', 'Friday'),
('S', 'Saturday Only', 'Saturday')
ON CONFLICT (name) DO NOTHING;

-- Insert common time slots (7:00 AM to 8:00 PM)
INSERT INTO time_slots (day_of_week, start_time, end_time) VALUES
('Monday', '07:00:00', '09:00:00'),
('Monday', '09:00:00', '11:00:00'),
('Monday', '11:00:00', '13:00:00'),
('Monday', '13:00:00', '15:00:00'),
('Monday', '15:00:00', '17:00:00'),
('Monday', '17:00:00', '19:00:00'),
('Tuesday', '07:00:00', '09:30:00'),
('Tuesday', '09:30:00', '12:00:00'),
('Tuesday', '13:00:00', '15:30:00'),
('Tuesday', '15:30:00', '18:00:00'),
('Wednesday', '07:00:00', '09:00:00'),
('Wednesday', '09:00:00', '11:00:00'),
('Wednesday', '11:00:00', '13:00:00'),
('Wednesday', '13:00:00', '15:00:00'),
('Wednesday', '15:00:00', '17:00:00'),
('Wednesday', '17:00:00', '19:00:00'),
('Thursday', '07:00:00', '09:30:00'),
('Thursday', '09:30:00', '12:00:00'),
('Thursday', '13:00:00', '15:30:00'),
('Thursday', '15:30:00', '18:00:00'),
('Friday', '07:00:00', '09:00:00'),
('Friday', '09:00:00', '11:00:00'),
('Friday', '11:00:00', '13:00:00'),
('Friday', '13:00:00', '15:00:00'),
('Friday', '15:00:00', '17:00:00'),
('Friday', '17:00:00', '19:00:00')
ON CONFLICT (day_of_week, start_time, end_time) DO NOTHING;

-- Insert default settings only if not exists
INSERT INTO settings (key, value, description, data_type) VALUES
('default_max_teaching_load', '24', 'Default maximum teaching load in units', 'integer'),
('default_max_sections', '6', 'Default maximum number of sections per faculty', 'integer'),
('allow_schedule_overlap', 'false', 'Allow schedule overlaps', 'boolean'),
('notification_enabled', 'true', 'Enable system notifications', 'boolean')
ON CONFLICT (key) DO NOTHING;
