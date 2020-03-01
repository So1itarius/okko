 ALTER TABLE FCT_PROD ENABLE ROW MOVEMENT;
 --ALTER TABLE FCT_PROD DISABLE ROW MOVEMENT;
 ALTER TABLE FCT_PROD SHRINK SPACE;
--ALTER TABLE FCT_PROD SHRINK SPACE [COMPACT][CASCADE];
--[COMPACT] не лочит таблицу и не понижает HWM
--[CASCADE] лочит таблицу и перенесоит все объекты таблицы
--ALTER TABLE FCT_PROD DEALLOCATE UNUSED KEEP block_size;

 SET SERVEROUTPUT ON
 
 declare
        VAR1 number;
        VAR2 number;
        VAR3 number;
        VAR4 number;
        VAR5 number;
        VAR6 number;
        VAR7 number;
begin
   SYS.dbms_space.unused_space('TEST_USER','FCT_PROD','TABLE',
                          VAR1,VAR2,VAR3,VAR4,VAR5,VAR6,VAR7);
   dbms_output.put_line('OBJECT_NAME       = SPACES');
   dbms_output.put_line('---------------------------');
   dbms_output.put_line('TOTAL_BLOCKS      = '||VAR1);
   dbms_output.put_line('TOTAL_BYTES       = '||VAR2);
   dbms_output.put_line('UNUSED_BLOCKS     = '||VAR3);
   dbms_output.put_line('UNUSED_BYTES      = '||VAR4);
   dbms_output.put_line('LAST_USED_EXTENT_FILE_ID  = '||VAR5);
   dbms_output.put_line('LAST_USED_EXTENT_BLOCK_ID = '||VAR6);
   dbms_output.put_line('LAST_USED_BLOCK   = '||VAR7);
end;
/