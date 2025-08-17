# 📊 Excel-Driven ETL Tool

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Pandas](https://img.shields.io/badge/Pandas-Latest-green.svg)](https://pandas.pydata.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-Latest-red.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A powerful, configuration-driven ETL tool that uses Excel spreadsheets to define data migration rules between databases.

## 🚀 Overview

The Excel-Driven ETL Tool simplifies database migration and data transformation processes by using Excel files as configuration templates. Instead of hard-coding migration logic, users can define source tables, destination schemas, column mappings, and transformation rules directly in an intuitive Excel interface.

### ✨ Key Features

- **📋 Excel Configuration**: Define ETL processes using familiar Excel spreadsheets
- **🔗 Multi-Database Support**: Works with PostgreSQL, MySQL, and other SQL databases via SQLAlchemy
- **🛡️ Secure Connection Management**: Database credentials stored in encrypted JSON files
- **✅ Column Validation**: Automatic validation of source columns against database schemas
- **📝 Comprehensive Logging**: Detailed execution logs for monitoring and debugging
- **⏱️ ETL Timestamp Tracking**: Automatic addition of processing timestamps to migrated data
- **🎯 Flexible Table Selection**: Process specific tables or entire database schemas

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│                 │    │                  │    │                 │
│  etl_driver.xlsx│───▶│ excel_driven_etl │───▶│ Destination DB  │
│  Configuration  │    │     Python       │    │                 │
│                 │    │     Script       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                        │                        ▲
         │                        ▼                        │
         │              ┌──────────────────┐               │
         │              │   secrets.json   │               │
         │              │   Credentials    │               │
         │              └──────────────────┘               │
         │                                                 │
         └─────────────────────────────────────────────────┘
                        Source Database
```

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager
- Access to source and destination databases

### Dependencies

```bash
pip install pandas sqlalchemy psycopg2-binary openpyxl requests
```

### Quick Setup

1. **Clone or download** the project files:
   ```bash
   git clone <your-repo-url>
   cd excel-driven-etl
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your databases** (see Configuration section below)

## ⚙️ Configuration

### 1. Database Credentials (`secrets.json`)

Create a `secrets.json` file with your database connection details:

```json
{
  "database_connections": {
    "source_db": {
      "host": "localhost",
      "database": "source_database",
      "username": "your_username",
      "password": "your_password",
      "db_type": "postgresql",
      "port": 5432
    },
    "dest_db": {
      "host": "localhost",
      "database": "destination_database",
      "username": "your_username",
      "password": "your_password",
      "db_type": "postgresql",
      "port": 5432
    }
  }
}
```

### 2. ETL Configuration (`etl_driver.xlsx`)

The Excel driver file contains multiple sheets:

#### **Config Sheet**
| Setting | Value | Description |
|---------|-------|-------------|
| source_db_key | source_db | Reference to connection in secrets.json |
| source_schema | public | Source database schema |
| dest_db_key | dest_db | Reference to destination connection |
| dest_schema | etl_schema | Destination database schema |

#### **Table Configuration Sheets**
Each additional sheet represents a table to migrate. Sheet names should match source table names.

**Example sheet "users":**
| Column_Name | New_Name | Filter |
|-------------|----------|---------|
| user_id | id | |
| first_name | fname | |
| last_name | lname | |
| email | email_address | |
| created_date | | |

## 🚀 Usage

### Basic Execution

```bash
python excel_driven_etl.py
```

### Command Line Options

The script accepts command-line arguments and generates detailed logs:

```bash
# Run with specific configuration
python excel_driven_etl.py

# Check logs
tail -f excel_driven_etl.log
```

### Execution Flow

1. **🔧 Initialization**: Load configuration and establish database connections
2. **📊 Validation**: Verify column existence in source tables
3. **🔄 Processing**: Extract data from source, transform as needed
4. **💾 Loading**: Insert transformed data into destination tables
5. **📝 Logging**: Generate comprehensive execution reports

## 📋 Features in Detail

### Column Validation
- Automatically validates Excel-defined columns against actual database schemas
- Provides detailed logging of matched and unmatched columns
- Continues processing with valid columns only

### Data Transformation
- Adds `ETL_DATE_TIME_ZONE` timestamp to all migrated records
- Supports column renaming (planned feature)
- Filtering capabilities (planned feature)

### Error Handling
- Comprehensive exception handling and logging
- Graceful handling of missing columns or tables
- Connection management and cleanup

## 📁 File Structure

```
excel-driven-etl/
├── excel_driven_etl.py      # Main ETL script
├── etl_driver.xlsx          # Excel configuration file
├── secrets.json             # Database credentials (create this)
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── excel_driven_etl.log     # Execution logs
```

## 🔮 Planned Enhancements

- [ ] **Column Renaming**: Use `New_Name` column for destination column names
- [ ] **Data Filtering**: Implement row-level filtering using `Filter` column
- [ ] **Table Prefixes/Suffixes**: Add configurable table name modifications
- [ ] **Progress Tracking**: Enhanced progress indicators and validation
- [ ] **Database Permissions**: Improved permission handling for destination schemas
- [ ] **Incremental Loading**: Support for delta/incremental data loads
- [ ] **Data Type Mapping**: Automatic data type conversion between databases

## 🐛 Troubleshooting

### Common Issues

**Connection Errors**
- Verify database credentials in `secrets.json`
- Check network connectivity to database servers
- Ensure proper database permissions

**Column Mismatch Errors**
- Review Excel column names against actual table schemas
- Check logs for specific unmatched columns
- Verify table names match sheet names exactly

**Permission Errors**
- Ensure destination database user has CREATE TABLE permissions
- Verify schema exists or user can create schemas

## 📊 Monitoring and Logs

The tool generates comprehensive logs including:
- Execution start/end times
- Connection establishment status
- Column validation results
- Data processing progress
- Error details and stack traces
- Performance metrics

Log file location: `excel_driven_etl.log`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Joseph P. Merten**
- Created: August 13, 2025
- Email: kc8son@yahoo.com
- GitHub: [kc8son](https://github.com/kc8son)

## 🙏 Acknowledgments

- Built with [Pandas](https://pandas.pydata.org/) for data manipulation
- Database connectivity powered by [SQLAlchemy](https://www.sqlalchemy.org/)
- Excel integration via [OpenPyXL](https://openpyxl.readthedocs.io/)

---

*Made with ❤️ for data engineers who love Excel configurations!*