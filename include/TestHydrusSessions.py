import ClientConstants as CC
import collections
import HydrusConstants as HC
import HydrusExceptions
import HydrusSessions
import os
import TestConstants
import unittest

class TestSessions( unittest.TestCase ):
    
    def test_server( self ):
        
        discard = HC.app.GetWrite( 'session' ) # just to discard gumph from testserver
        
        session_key_1 = os.urandom( 32 )
        service_key = os.urandom( 32 )
        
        permissions = [ HC.GET_DATA, HC.POST_DATA, HC.POST_PETITIONS, HC.RESOLVE_PETITIONS, HC.MANAGE_USERS, HC.GENERAL_ADMIN, HC.EDIT_SERVICES ]
        
        account_id = 1
        account_type = HC.AccountType( 'account', permissions, ( None, None ) )
        created = HC.GetNow() - 100000
        expiry = None
        used_data = ( 0, 0 )
        
        account = HC.Account( account_id, account_type, created, expiry, used_data )
        
        expiry = HC.GetNow() - 10
        
        HC.app.SetRead( 'sessions', [ ( session_key_1, service_key, account, expiry ) ] )
        
        session_manager = HydrusSessions.HydrusSessionManagerServer()
        
        with self.assertRaises( HydrusExceptions.SessionException ):
            
            session_manager.GetAccount( service_key, session_key_1 )
            
        
        #
        
        expiry = HC.GetNow() + 10000
        
        HC.app.SetRead( 'sessions', [ ( session_key_1, service_key, account, expiry ) ] )
        
        session_manager = HydrusSessions.HydrusSessionManagerServer()
        
        read_account = session_manager.GetAccount( service_key, session_key_1 )
        
        self.assertIs( read_account, account )
        
        #
        
        expiry = None
        
        account_2 = HC.Account( 2, account_type, created, expiry, used_data )
        
        HC.app.SetRead( 'account', account_2 )
        
        account_identifier = HC.AccountIdentifier( access_key = os.urandom( 32 ) )
        
        ( session_key_2, expiry_2 ) = session_manager.AddSession( service_key, account_identifier )
        
        [ ( args, kwargs ) ] = HC.app.GetWrite( 'session' )
        
        ( written_session_key, written_service_key, written_account, written_expiry ) = args
        
        self.assertEqual( ( session_key_2, service_key, account_2, expiry_2 ), ( written_session_key, written_service_key, written_account, written_expiry ) )
        
        read_account = session_manager.GetAccount( service_key, session_key_2 )
        
        self.assertIs( read_account, account_2 )
        
        #
        
        HC.app.SetRead( 'account', account )
        
        account_identifier = HC.AccountIdentifier( access_key = os.urandom( 32 ) )
        
        ( session_key_3, expiry_3 ) = session_manager.AddSession( service_key, account_identifier )
        
        [ ( args, kwargs ) ] = HC.app.GetWrite( 'session' )
        
        ( written_session_key, written_service_key, written_account, written_expiry ) = args
        
        self.assertEqual( ( session_key_3, service_key, account, expiry_3 ), ( written_session_key, written_service_key, written_account, written_expiry ) )
        
        read_account = session_manager.GetAccount( service_key, session_key_3 )
        
        self.assertIs( read_account, account )
        
        #
        
        expiry = None
        
        updated_account = HC.Account( 1, account_type, created, expiry, ( 1, 1 ) )
        
        HC.app.SetRead( 'account', updated_account )
        
        account_identifier = HC.AccountIdentifier( access_key = os.urandom( 32 ) )
        
        session_manager.RefreshAccounts( service_key, [ account_identifier ] )
        
        read_account = session_manager.GetAccount( service_key, session_key_1 )
        
        self.assertIs( read_account, updated_account )
        
        read_account = session_manager.GetAccount( service_key, session_key_3 )
        
        self.assertIs( read_account, updated_account )
        
        #
        
        expiry = None
        
        updated_account_2 = HC.Account( 1, account_type, created, expiry, ( 2, 2 ) )
        
        HC.app.SetRead( 'sessions', [ ( session_key_1, service_key, updated_account_2, expiry ), ( session_key_2, service_key, account_2, expiry ), ( session_key_3, service_key, updated_account_2, expiry ) ] )
        
        session_manager.RefreshAllAccounts()
        
        read_account = session_manager.GetAccount( service_key, session_key_1 )
        
        self.assertIs( read_account, updated_account_2 )
        
        read_account = session_manager.GetAccount( service_key, session_key_2 )
        
        self.assertIs( read_account, account_2 )
        
        read_account = session_manager.GetAccount( service_key, session_key_3 )
        
        self.assertIs( read_account, updated_account_2 )
        