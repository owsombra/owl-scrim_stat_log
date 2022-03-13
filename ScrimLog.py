import pandas as pd 
import os 
import pymysql
from TraditionalStat import *
from AdvancedStat import * 
from TeamfightDetector import *
from PeriEventTimeHistogram import *
from MySQLConnection import *
from MapNameList import *
from sqlalchemy import exc
from mysql_auth import mysql_auth

class ScrimLog():
    def __init__(self, teamname=None, tablename=None):
        if tablename is None or teamname is None:
            pass 
        else:
            self.teamname = teamname
            self.rawdb_dbname = teamname + '_Rawdb'
            self.tablename = tablename
            self.match_id = tablename[0:11] # match_id: '(yyyymmdd)_(scrimNum)' (e.g. 20200318_02)
            # define num_map
            mapname = tablename.split('_')[3].split('.')[0]
            if mapname in mapnamelist:
                self.num_map = 1
            else: 
                self.num_map = mapname[-1]
            #self.set_directory()
            #self.set_df_input()
            self.set_table_df_list(tablename)
            self.set_index()
            self.set_WorkshopStat()
            self.set_TraditionalStat()
            self.set_AdvancedStat()
            self.set_TeamfightDetector()
            self.set_FinalStatIndex()

    def set_directory(self):
        '''
        Csv file naming convention:     '(yyyy:mm:dd)_(scrimNum)_(enemyTeamName)_(mapName)' e.g. '20210318_02_O2_Oasis'
        MatchId:   '(yyyy:mm:dd)_(scrimNum)' e.g. '20210318_02'
        '''
        path = 'G:/공유 드라이브/NYXL Scrim Log/Csv'
        self.filepath = os.path.join(path, self.csvname)

    def set_df_input(self):
        self.df_input = pd.read_csv(self.filepath)
        
    def set_table_df_list(self, tablename):
        db_login = mysql_auth.auth_info
        db_conn = pymysql.connect(host = db_login['hostname'], port = int(db_login['port']), user = db_login['username'], passwd = db_login['pwd'], db = self.rawdb_dbname)
        table_df = pd.read_sql(
        sql=f"SELECT * FROM `{tablename}` order by Timestamp asc",
        con=db_conn,
        )
        #del table_df['id']
        db_conn.close()
        
        #return table_df_list    
        table_df = table_df.astype({
            'HeroDamageDealt': 'float',
            'BarrierDamageDealt': 'float',
            'DamageBlocked': 'float',
            'DamageTaken': 'float',
            'Deaths': 'int',
            'Eliminations': 'int',
            'FinalBlows': 'int',
            'EnvironmentalDeaths': 'int',
            'EnvironmentalKills': 'int',
            'HealingDealt': 'float',
            'ObjectiveKills': 'int',
            'SoloKills': 'int',
            'UltimatesEarned': 'int',
            'UltimatesUsed': 'int',
            'UltimateCharge': 'int',
            'Cooldown1': 'float',
            'Cooldown2': 'float',
            'CooldownSecondaryFire': 'float',
            'CooldownCrouching': 'float',
            'IsAlive': 'int',
            'MaxHealth': 'float',
            'Health': 'float',
            'DefensiveAssists': 'int',
            'OffensiveAssists': 'int',
            'IsBurning': 'int',
            'IsKnockedDown': 'int',
            'IsAsleep': 'int',
            'IsFrozen': 'int',
            'IsUnkillable': 'int',
            'IsInvincible': 'int',
            'IsRooted': 'int',
            'IsStunned': 'int',
            'IsHacked': 'int',
            'HealingReceived': 'float'
        })

        self.df_input = table_df
        
    def set_index(self):
        # df_init
        self.df_init = self.df_input 
        
        # match_id
        self.df_init['MatchId'] = self.match_id

        # num_map
        self.df_init['num_map'] = self.num_map

        # team name
        #NYE_alt_names = ['NYXL', 'Team 1', '1팀', 'New York Excelsior', 'New York']
        team_one_name = self.df_init['Team'].unique()[0]
        team_two_name = self.df_init['Team'].unique()[1]

        '''
        if team_one_name == 'NYE':
            pass
        elif team_one_name in NYE_alt_names:
            self.df_init['Team'] = self.df_init['Team'].replace({team_one_name:'NYE'})
            team_one_name = 'NYE'
        elif team_two_name == 'NYE':
            team_one_name = self.df_init['Team'].unique()[1]
            team_two_name = self.df_init['Team'].unique()[0]
        elif team_two_name in NYE_alt_names:
            self.df_init['Team'] = self.df_init['Team'].replace({team_two_name:'NYE'})
            team_one_name = self.df_init['Team'].unique()[1]
            team_two_name = 'NYE'
        else:
            raise Exception('NYE is not designated as Team 1. Check the Team names')
        '''
        
        self.team_one_name = team_one_name
        self.team_two_name = team_two_name
        
        # idx_col
        self.idx_col = ['MatchId', 'num_map', 'Map', 'Section', 'Timestamp', 'Team', 'RoundName', 'Point', 'Player', 'Hero']

        # text_based col 
        self.text_based_col = ['Position', 'DeathByHero', 'DeathByAbility', 'DeathByPlayer', 'Resurrected', 'DuplicatedHero', 'DuplicateStatus', 'FacingDirection', 'Team1Player1InViewAngle','Team1Player2InViewAngle','Team1Player3InViewAngle','Team1Player4InViewAngle','Team1Player5InViewAngle','Team2Player1InViewAngle','Team2Player2InViewAngle','Team2Player3InViewAngle','Team2Player4InViewAngle','Team2Player5InViewAngle']

    def set_WorkshopStat(self):
        df_WorkshopStat = self.df_init.set_index(self.idx_col)
        self.df_text_based_col = df_WorkshopStat[self.text_based_col]
        self.df_WorkshopStat = df_WorkshopStat.drop(columns=self.text_based_col)        
    
    def set_TraditionalStat(self):

        # TimePlayed        
        df_TraditionalStat = TimePlayed(self.df_WorkshopStat).get_df_result()
        # AllDamageDealt
        df_TraditionalStat = AllDamageDealt(df_TraditionalStat).get_df_result()
        # HealingReceived
        df_TraditionalStat = HealingReceived(df_TraditionalStat).get_df_result()
        # Cooldown1Percent
        df_TraditionalStat = Cooldown1Percent(df_TraditionalStat).get_df_result()
        # Cooldown2Percent
        df_TraditionalStat = Cooldown2Percent(df_TraditionalStat).get_df_result()
        # CooldownSecondaryFirePercent
        df_TraditionalStat = CooldownSecondaryFirePercent(df_TraditionalStat).get_df_result()
        # CooldownCrouchingPercent
        df_TraditionalStat = CooldownCrouchingPercent(df_TraditionalStat).get_df_result()
        # HealthPercent
        df_TraditionalStat = HealthPercent(df_TraditionalStat).get_df_result() # Health column 추가되면 진행
        # NumAlive
        df_TraditionalStat = NumAlive(df_TraditionalStat).get_df_result()
        # dx
        '''
        현재 스크림 워크샵이 영웅별로 스탯을 누적해주는 것이 아니라 플레이어 별로 스탯을 누적해주기 때문에 
        선수가 도중에 영웅을 바꿀 경우 diff() 함수에서 문제가 발생 
        --> `hero_col` 따로 빼서 diff() 구하고 나중에 merge로 해결
        '''
        def diff_stat(df_input=None):
            diff_stat_list = [] # define stat names to diff()
            df_init = df_input.reset_index()
            grouping = [x for x in self.idx_col if x not in ['Hero', 'Point']]
            hero_col = df_init.set_index(grouping)['Hero']
            df_group = df_init.groupby(by=grouping).sum()
            dx = df_group.groupby([x for x in grouping if x != 'Timestamp']).diff().fillna(0)
            df_merge = pd.merge(df_group, dx, how='outer', left_index=True, right_index=True, suffixes=('', '/s'))
            df_merge = pd.merge(df_merge, hero_col, how='outer', left_index=True, right_index=True) # add hero_co
            return df_merge
        
        # calculate dx table and merge
        df_TraditionalStat = diff_stat(df_input=df_TraditionalStat)

        # indexing
        df_TraditionalStat = df_TraditionalStat.groupby(by=self.idx_col).max()
        
        self.df_TraditionalStat = df_TraditionalStat

    def set_AdvancedStat(self):
        # RCP
        df_AdvancedStat = RCPv1(self.df_TraditionalStat).get_df_result()
        # FB_value         
        df_AdvancedStat = FBValue(df_AdvancedStat).get_df_result()
        # Death_risk
        df_AdvancedStat = DeathRisk(df_AdvancedStat).get_df_result()
        # New AdvancedStat here
        # indexing
        df_AdvancedStat = df_AdvancedStat.groupby(by=self.idx_col).max()
        
        self.df_AdvancedStat = df_AdvancedStat
    
    def set_TeamfightDetector(self):
        df_TFStat = TeamfightDetector(self.df_AdvancedStat).get_df_result()
        # indexing
        df_TFStat = df_TFStat.groupby(by=self.idx_col).max()
        
        # DominanceIndex
        df_TFStat = DIv2(df_TFStat).get_df_result()
        self.df_TFStat = df_TFStat
    
    def set_FinalStatIndex(self):
        df_FinalStat = self.df_TFStat.reset_index()
        df_FinalStat = df_FinalStat.groupby(by=self.idx_col).max()
        # add Text-based columns
        df_FinalStat = pd.merge(df_FinalStat, self.df_text_based_col, left_index=True, right_index=True)
        # Echo Duplicate
        def EchoDuplicate(df_FinalStat):
            if 'DuplicateStatus' in df_FinalStat.columns:
                F_Duplicating = df_FinalStat[['DuplicateStatus']].replace('DUPLICATING', 1).fillna(0)
                F_Duplicating = df_FinalStat[['DuplicateStatus']].replace('', 0).fillna(0)
                F_Duplicating.rename(columns={'DuplicateStatus':'IsEchoUlt'}, inplace=True)
                IsEchoUlt = F_Duplicating.groupby(['MatchId', 'Map', 'Section', 'Player', 'Hero']).diff().fillna(0)
                result = pd.merge(df_FinalStat, IsEchoUlt, left_index=True, right_index=True)
            else:
                df_FinalStat['DuplicateStatus'] = 0
                result = df_FinalStat
            return result 

        df_FinalStat = EchoDuplicate(df_FinalStat)

        self.df_FinalStat = df_FinalStat

    def get_df_FinalStat(self):
        return self.df_FinalStat
    
    def get_TF_info(self):
        return self.TF_info

    def export_to_csv(self, save_dir='C:/Users/Sqix_OW/Desktop'):
        self.df_FinalStat.to_csv(save_dir + f'FinalStat_{self.csvname}')
    
    def update_FinalStat_to_csv(self, save_dir=r'G:\공유 드라이브\NYXL Scrim Log\FinalStat/'):
        # set path
        filepath = r'G:/공유 드라이브/NYXL Scrim Log/Csv/'
        filelist = os.listdir(filepath)
        csv_filelist = [x for x in filelist if x.endswith('.csv')]
        updated_csv = 'FilesUpdated_FinalStat.txt'
        
        # open updated filelist
        f = open(filepath + updated_csv, 'r+')
        lines = f.readlines()
        updated_filelist = []

        for line in lines:
            updated_filelist.append(line.replace('\n', ''))

        # sort files to be updated
        csv_filelist_to_update = list(set(csv_filelist) - set(updated_filelist))
        csv_filelist_to_update.sort()

        # export to csv in FinalStat folder
        for filename in csv_filelist_to_update:
            ScrimLog(filename).export_to_csv()

            f.write(filename+'\n')
            print(f'File Exported: {filename}')

        f.close()

    def update_FinalStat_to_sql(self, teamname):
        rawdb_dbname = teamname + '_Rawdb'
        def get_update_tablelist():
            sql = """
                select tablename from toFinalstatTable where isReflected = false;
            """
            db_login = mysql_auth.auth_info
            db_conn = pymysql.connect(host = db_login['hostname'], port = int(db_login['port']), user = db_login['username'], passwd = db_login['pwd'], db = rawdb_dbname)
            cursor = db_conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            update_list = []
            for row_data in result:
                update_list.append(row_data[0])
            
            db_conn.close()
            #return update_list
            return update_list

        update_list = get_update_tablelist()
        db_login = mysql_auth.auth_info
        rawdb_conn = pymysql.connect(host = db_login['hostname'], port = int(db_login['port']), user = db_login['username'], passwd = db_login['pwd'], db = rawdb_dbname)
        cursor = rawdb_conn.cursor()
        for tablename in update_list:
            scrimlog = ScrimLog(teamname, tablename)
            df_sql = MySQLConnection(dbname=teamname, input_df=scrimlog.df_FinalStat.reset_index()) # reset_index to export to mysql db
            check_update_sql = 'update toFinalstatTable set isReflected = true where tablename = \'' + tablename + '\';';
            print(check_update_sql)
            try: # Insert dataframe into DB except duplicated primary keys
                df_sql.export_to_db(table_name='finalstat', if_exists='append')
                cursor.execute(check_update_sql)
                print(f'File Exported to {df_sql.dbname}: {tablename}')
            except exc.IntegrityError:
                cursor.execute(check_update_sql)
                print('IntegrityError')
            finally:
                rawdb_conn.commit()
        
        rawdb_conn.close()
        


