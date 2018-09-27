--determine friend request acceptance rate, but account for duplicates in either table (the requests or the accepts)
select round(ifnull((count(distinct(concat(sender_id, send_to_id)))/(select count(distinct(concat(sender_id,send_to_id))) from friend_request)),0.0),2) as accept_rate
FROM friend_request
where exists (select * from request_accepted where request_accepted.requester_id = friend_request.sender_id and friend_request.send_to_id = request_accepted.accepter_id);
