#!/bin/bash
host_default="https://lb-fullnode.incognito.org/fullnode"
host_local="http://localhost:8334"
host=$host_default
watch_time=2
verbose=""
while getopts "hvwe:i:" option; do
   case "$option" in
      "e")
         [[ ${OPTARG} == "local" ]] && host=$host_local || host=${OPTARG}
         ;;
      "v")
         verbose=1
         ;;
      "w")
         watch=1
         ;;
      "i")
         watch_time=${OPTARG}
         ;;
      "h")
cat << EOF
   $(basename $0) [-e END_POINT] [-vw] [-i INTERVAL]
      -e END_POINT: endpoint to get info. default value: $host_default.
         Special value: local=$host_local.
      -v: verbose, more info output.
      -w: watch mode, keep getting info every {i} second.
      -i INTERVAL: watch interval, only work with -w.
      -h: print this help message then exit.
   Example:
      $(basename $0) -e local -vwt 10
   or
      $(basename $0) -e http://myendpoint.com:9876 -v
EOF
         exit
         ;;
      ?)
         exit
         ;;
   esac
done

function get_chain_info {
   blc_info='{ "jsonrpc":"1.0", "method":"getblockchaininfo", "params":[], "id":1 }'
   info=$(curl -s --header "Content-Type: application/json" \
      --request POST \
       --data "$blc_info" $1)

   if [[ -z $info ]]; then
      echo "!!! Got no info, Check your endpoint, make sure it's correct: $1"
      exit
   fi

   activeShards=$(echo $info | jq '.Result.ActiveShards')

   echo $1
   if [[ $2 ]]; then

      #format info
      max_e_len=0
      max_h_len=0
      for (( i=-1; i<$activeShards; i++ )) ; do
         height=$(echo $info | jq '.Result.BestBlocks."'$i'".Height')
         epoch=$(echo $info | jq '.Result.BestBlocks."'$i'".Epoch')

         max_e_len=$(( $max_e_len < ${#epoch} ? ${#epoch} : $max_e_len ))
         max_h_len=$(( $max_h_len < ${#epoch} ? ${#epoch} : $max_h_len ))

      done

      # print info
      for (( i=-1; i<$activeShards; i++ )) ; do
         height=$(echo $info | jq '.Result.BestBlocks."'$i'".Height')
         epoch=$(echo $info | jq '.Result.BestBlocks."'$i'".Epoch')
         hash=$(echo $info | jq '.Result.BestBlocks."'$i'".Hash')
         printf "%2s : %${max_e_len}s | %${max_h_len}s | %s\n" ${i} ${epoch} ${height} ${hash}
      done
      return
   fi


   for (( i=-1; i<$activeShards; i++ )) ; do
      height=$(echo $info | jq '.Result.BestBlocks."'$i'".Height')
      printf "%3s: %s\n" $i $height
   done
}

if [[ $watch ]]; then
   export -f get_chain_info
   watch -n $watch_time -d -x bash -c "get_chain_info $host $verbose"
else
   get_chain_info $host $verbose
fi
