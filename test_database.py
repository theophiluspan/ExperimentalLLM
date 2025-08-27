# test_database.py - Complete Test Script with Expected Output

from database import create_database, AdminUtils
import os

def test_database():
    """
    This function tests all major database functionality.
    
    What it does:
    1. Creates a database and tables if they don't exist
    2. Tests condition assignment (should alternate Control/Warning)
    3. Tests statistics collection
    4. Tests admin utilities
    5. Tests data export functionality
    """
    
    print("🧪 Testing AI Survey Database")
    print("=" * 50)
    
    # Test 1: Database Creation
    print("\n📁 Test 1: Database Creation")
    try:
        db = create_database()
        print("   ✅ Database created successfully")
        
        # Check if database file was created
        if os.path.exists('survey_data.db'):
            print("   ✅ Database file (survey_data.db) exists")
            file_size = os.path.getsize('survey_data.db')
            print(f"   📊 Database file size: {file_size} bytes")
        else:
            print("   ❌ Database file not found")
            
    except Exception as e:
        print(f"   ❌ Database creation failed: {e}")
        return False
    
    # Test 2: Condition Assignment (This is the core test)
    print("\n📋 Test 2: Condition Assignments")
    print("   Testing alternating assignment pattern...")
    
    expected_pattern = [
        "Control",                    # 1st participant
        "Group A - Warning Label",    # 2nd participant  
        "Control",                    # 3rd participant
        "Group A - Warning Label",    # 4th participant
        "Control",                    # 5th participant
        "Group A - Warning Label"     # 6th participant
    ]
    
    actual_assignments = []
    
    try:
        for i in range(6):
            condition, participant_id = db.get_next_condition()
            actual_assignments.append(condition)
            print(f"   Participant {participant_id}: {condition}")
            
            # Verify it matches expected pattern
            if condition == expected_pattern[i]:
                print(f"      ✅ Correct (expected {expected_pattern[i]})")
            else:
                print(f"      ❌ Wrong (expected {expected_pattern[i]}, got {condition})")
        
        # Check overall pattern
        if actual_assignments == expected_pattern:
            print("   ✅ Assignment pattern is correct!")
        else:
            print("   ❌ Assignment pattern is wrong!")
            print(f"   Expected: {expected_pattern}")
            print(f"   Got:      {actual_assignments}")
            
    except Exception as e:
        print(f"   ❌ Condition assignment failed: {e}")
        return False
    
    # Test 3: Statistics
    print("\n📊 Test 3: Statistics Collection")
    try:
        stats = db.get_assignment_stats()
        print("   Current database statistics:")
        print(f"     Total participants: {stats['total_participants']}")
        print(f"     Control group: {stats['control_count']}")
        print(f"     Warning group: {stats['warning_count']}")
        print(f"     Balance difference: ±{stats['balance_difference']}")
        
        # Verify the numbers make sense
        expected_total = 6  # We just added 6 participants
        expected_control = 3  # Should be 3 control
        expected_warning = 3  # Should be 3 warning
        
        if (stats['total_participants'] >= expected_total and 
            stats['control_count'] >= expected_control and 
            stats['warning_count'] >= expected_warning):
            print("   ✅ Statistics look correct")
        else:
            print("   ❌ Statistics seem wrong")
            
    except Exception as e:
        print(f"   ❌ Statistics collection failed: {e}")
        return False
    
    # Test 4: Admin Utilities
    print("\n👨‍💼 Test 4: Admin Utilities")
    try:
        admin = AdminUtils()
        detailed_stats = admin.show_detailed_stats()
        
        print("   Admin dashboard data:")
        basic_stats = detailed_stats['basic_stats']
        progress = detailed_stats['progress']
        
        print(f"     Total participants: {basic_stats['total_participants']}")
        print(f"     Progress toward 30: {progress['current_total']}/30 ({progress['progress_percentage']:.1f}%)")
        print(f"     Remaining needed: {progress['remaining']}")
        
        if basic_stats['total_participants'] > 0:
            print("   ✅ Admin utilities working")
        else:
            print("   ❌ Admin utilities not working")
            
    except Exception as e:
        print(f"   ❌ Admin utilities failed: {e}")
        return False
    
    # Test 5: Data Export
    print("\n📤 Test 5: Data Export")
    try:
        participants_df, responses_df = db.export_data()
        
        print(f"   Participants table: {len(participants_df)} rows, {len(participants_df.columns)} columns")
        if len(participants_df) > 0:
            print(f"   Participant columns: {list(participants_df.columns)}")
            print(f"   Sample participant data:")
            print(f"     ID: {participants_df.iloc[0]['id']}")
            print(f"     Condition: {participants_df.iloc[0]['condition']}")
        
        print(f"   Responses table: {len(responses_df)} rows, {len(responses_df.columns)} columns")
        
        if len(participants_df) >= 6:
            print("   ✅ Data export working")
        else:
            print("   ❌ Data export has wrong number of rows")
            
    except Exception as e:
        print(f"   ❌ Data export failed: {e}")
        return False
    
    # Test 6: File Export (CSV)
    print("\n📁 Test 6: CSV File Export")
    try:
        admin = AdminUtils()
        participants_file, responses_file = admin.export_for_analysis("test_export")
        
        if os.path.exists(participants_file) and os.path.exists(responses_file):
            print(f"   ✅ CSV files created:")
            print(f"     {participants_file}")
            print(f"     {responses_file}")
            
            # Clean up test files
            os.remove(participants_file)
            os.remove(responses_file)
            print("   🧹 Test files cleaned up")
        else:
            print("   ❌ CSV export failed")
            
    except Exception as e:
        print(f"   ❌ CSV export failed: {e}")
        return False
    
    # Final Summary
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print(f"📊 Database contains {stats['total_participants']} test participants")
    print("🚀 Your database is ready for the Streamlit app!")
    print("\nTo clean up test data, you can delete 'survey_data.db' file")
    
    return True

def cleanup_test_data():
    """Remove test data if you want to start fresh"""
    if os.path.exists('survey_data.db'):
        response = input("\nDo you want to delete test data? (y/N): ")
        if response.lower() == 'y':
            os.remove('survey_data.db')
            print("🧹 Test database deleted. You're ready to start fresh!")
        else:
            print("Test data kept. Your Streamlit app will continue from where tests left off.")

if __name__ == "__main__":
    success = test_database()
    
    if success:
        cleanup_test_data()
    else:
        print("\n❌ TESTS FAILED!")
        print("Check the error messages above to fix your database.py file")