#!/bin/bash
#
#
#	by jtxiao

MOTD=mmchuxing.com
OS_PLATFORM=`uname -i`

# platform=64bit
platform64(){
    echo 'auth required /lib64/security/pam_userdb.so db=/etc/vsftpd/vsftpd_login'  > /etc/pam.d/vsftpd.vu
    echo 'account required /lib64/security/pam_userdb.so db=/etc/vsftpd/vsftpd_login' >> /etc/pam.d/vsftpd.vu
}

# platform=32bit
platform32(){
    echo 'auth required /lib/security/pam_userdb.so db=/etc/vsftpd/vsftpd_login'  > /etc/pam.d/vsftpd.vu
    echo 'account required /lib/security/pam_userdb.so db=/etc/vsftpd/vsftpd_login' >> /etc/pam.d/vsftpd.vu
}

main_config(){
cat > /etc/vsftpd/vsftpd.conf <<EOF
anonymous_enable=NO
local_enable=YES
#write_enable=NO
dirmessage_enable=YES
xferlog_enable=YES
xferlog_file=/var/log/vsftpd.log
connect_from_port_20=YES
xferlog_std_format=YES
listen=YES
listen_port=21
userlist_enable=YES
chroot_local_user=YES
tcp_wrappers=YES
guest_enable=YES
#guest_username=ftp
pam_service_name=vsftpd.vu
user_config_dir=/etc/vsftpd/vsftpd_vu_conf
virtual_use_local_privs=YES
pasv_min_port=65000
pasv_max_port=65010
pasv_enable=yes
max_clients=200
max_per_ip=4
idle_session_timeout=600
ftpd_banner=Welcome to $MOTD FTP Service.
EOF
}
suport_ssl(){
    # fix ssl dependent
    cd /etc/pki/tls/certs
    make vsftpd.pem
    cp -a vsftpd.pem /etc/vsftpd/
    chmod 600 /etc/vsftpd/vsftdp.pem
    # vsftp ssl suport config
    cat >> /etc/vsftpd/vsftpd.conf <<EOF
# SSL Suport
ssl_enable=YES
allow_anon_ssl=NO
force_local_data_ssl=YES
force_local_logins_ssl=YES
ssl_tlsv1=YES
ssl_sslv2=YES
ssl_sslv3=YES
require_ssl_reuse=NO
ssl_ciphers=HIGH
rsa_cert_file=/etc/vsftpd/vsftpd.pem
#是否启用隐式ssl功能，不建议开启
#implicit_ssl=YES
##隐式ftp端口设置，如果不设置，默认还是21，但是当客户端以隐式ssl连接时，默认会使用990端口，导致连接失败！！
#listen_port=990
##输出ssl相关的日志信息
EOF
}
vu_config(){
    cat > /etc/vsftpd/vsftpd_vu_conf/$V_USER <<EOF
write_enable=YES
anonymous_enable=NO
anon_world_readable_only=NO
anon_upload_enable=YES
anon_mkdir_write_enable=YES
anon_other_write_enable=YES
local_umask=022
download_enable=Yes
guest_username=$1
local_root=$2
EOF
}
usage(){
    echo ""
    echo "usage: $0 <ftp user> <virtual username> <password> <workspace directory> [ssl|motd]"
    echo ""
    echo ""
    echo ""
    echo ""
    echo "-------------"
}
main(){
    if [ $# -ne 0 ]; then
        usage
    else
	read -p 'Input ftp home directory path:' WORKSPACE
	read -p 'Input virtual user:' V_USER
	read -p 'Input virtual user password:' V_U_PWD
	read -p 'Input guest user name:' USER
	read -p 'Input SSL to support ssl:' SSL
	# install ftp software
	yum install -y vsftpd db4-utils |tee  >> vsftpd-install.log
	# configruetion virtual user
	echo -e "${V_USER}\n${V_U_PWD}" > ./.ftpuser.list
	db_load -T -t hash -f ./.ftpuser.list /etc/vsftpd/vsftpd_login.db
	chmod 600 /etc/vsftpd/vsftpd_login.db
	cp /etc/vsftpd/vsftpd.conf{,.bak}
	# v_user config directory
	mkdir -p /etc/vsftpd/vsftpd_vu_conf
	if [ $OS_PLATFORM == "x86_64" ];then
	    platform64
	else
	    platform32
	fi
	main_config
	if [ -n "$SSL"  ];then
	    suport_ssl
	fi
	vu_config $USER $WORKSPACE
    fi
}
main
[ $? -ne 0 ] && echo "Deploy OK!"

