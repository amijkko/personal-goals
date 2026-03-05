# KYT Office - API Guide v1.4.pdf
*Added: 2026-03-05 16:09*
*Project: Custody*
*File ID: BQACAgIAAxkBAAOmaamqjmmiDnujfLn7J3V2TMWHZXsAArqQAAKH9EhJWNlv2dzt21Y6BA*

## Summary
1. **Описание сервиса**: KYT Office от BitOK позволяет регистрировать все криптовалютные переводы и контролировать их свойства и риски.

2. **Типы переводов**: Существует два основных типа переводов: полные переводы (уже произошедшие в блокчейне) и попытки перевода (еще не состоявшиеся). Полные переводы делятся на депозиты и выводы, а попытки - на попытки депозита и вывода.

3. **Регистрация переводов**: Для регистрации полного перевода необходимо использовать API-метод `/transfers/register/`, указав такие параметры, как `client_id`, `direction`, `network`, `tx_hash`, `token_id` и `output_address`.

4. **Пример запроса и ответа**: Пример запроса на регистрацию полного перевода и ответ от сервиса, который включает информацию о зарегистрированном переводе, его статусе и уровне риска.

5. **Обогащение состояния перевода**: После связывания транзакции состояние перевода обновляется с необходимыми свойствами, включая уровень риска и информацию о контрагенте.

## Full Text
Welcome to KYT Office by BitOK
KYT Office is the service where you can register all transfers in crypto and then control all its
properties and risks.

API Guide
Transfers
Transfers are core objects of KYT Service.

Types of transfers
There are two types of transfers:
-​

Full transfer - a transfer that has already occurred in a blockchain. The network, the
transaction hash, the input and output addresses, the amount and the accurate date
and time are defined.

-​

Transfer attempt - a transfer not yet occurred in a blockchain. Such types of
transfers are used to pre-check a counterparty wallet for potential risks.

There are 2 subtypes of the full transfers:
-​

Deposit - incoming transfer bound to a transaction.

-​

Withdrawal - outgoing transfer bound to a transaction.

There are 2 subtypes of the transfer attempts:
-​

Deposit attempt - incoming transfer not bound to a transaction.

-​

Withdrawal attempt - outgoing transfer not bound to a transaction.

Registering transfers
How to register a full transfer
To register a full transfer using /transfers/register/ endpoint you must define the following
fields about the transfer:
-​

client_id (optional) - an external ID of the client the transfer will be associated with.

-​

direction - the direction of the transfer.

-​

network - the code of the network where the transfer occurred.

-​

tx_hash - the hash of the transaction the transfer belongs to.

-​

token_id - the identifier of the token within its network.

-​

output_address - the address of a recipient of the transfer.

Request:

curl -X POST "https://kyt-api.bitok.org/v1/transfers/register/" \
--header "Content-Type: application/json" \
--header "Accept: application/json" \
--header "API-KEY-ID:{KEY_ID}" \
--header "API-TIMESTAMP:{TIMESTAMP}" \
--header "API-SIGNATURE:{SIGNATURE}" \
--data ‘{
"client_id": "id0001",
"direction": "incoming",
"network": "ETH",
"tx_hash": "0x46bf4313a1f7f22cf97859d119c609fedad81541330de661f967795cc4f46e89",
"token_id": "0xdac17f958d2ee523a2206206994597c13d831ec7",
"output_address": "0x98Cb5718876AaB18e3A8429a18Ad543f6369A6f3"
}’

Response:

{
"id": "cdc3fd93-c975-4b79-beb7-4ad058078b48",
"client_id": "id0001",
"registered_at": "2023-12-18T13:47:25.197606+03:00",
"occurred_at": null,
"direction": "incoming",
"risk_level": "undefined",
"network": "ETH",
"token_id": "0xdac17f958d2ee523a2206206994597c13d831ec7",
"token_symbol": "USDT",
"tx_hash": "0x46bf4313a1f7f22cf97859d119c609fedad81541330de661f967795cc4f46e89",
"tx_status": "binding",
"input_address": null,
"output_address": "0x98cb5718876aab18e3a8429a18ad543f6369a6f3",
"amount": null,
"fiat_currency": "USD",
"value_in_fiat": null,
"check_state": {
​
"exposure": "queued",
​
"exposure_checked_at": null,
​
"counterparty": "none",
​
"counterparty_checked_at": null,
​
"sanctions": "none",
​
"sanctions_checked_at": null

}
}

When the transaction is bound the state of the transfer state will be enriched with all
necessary properties.
Request:

curl -X GET "https://kyt-api.bitok.org/v1/transfers/cdc3fd93-c975-4b79-beb7-4ad058078b48/" \
--header "Accept: application/json" \
--header "API-KEY-ID:{KEY_ID}" \
--header "API-TIMESTAMP:{TIMESTAMP}" \
--header "API-SIGNATURE:{SIGNATURE}"

Response:

{
"id": "cdc3fd93-c975-4b79-beb7-4ad058078b48",
"client_id": "id0001",
"registered_at": "2023-12-18T13:47:25.197606+03:00",
"occurred_at": "2023-12-18T13:46:23+03:00",
"direction": "incoming",
"risk_level": "medium",
"network": "ETH",
"token_id": "0xdac17f958d2ee523a2206206994597c13d831ec7",
"token_symbol": "USDT",
"tx_hash": "0x46bf4313a1f7f22cf97859d119c609fedad81541330de661f967795cc4f46e89",
"tx_status": "bound",
"input_address": "0x56eddb7aa87536c09ccc2793473599fd21a8b17f",
"output_address": "0x98cb5718876aab18e3a8429a18ad543f6369a6f3",
"amount": 1206,
"fiat_currency": "USD",
"value_in_fiat": 1205.2,
"check_state": {
"exposure": "checked",
"exposure_checked_at": "2023-12-18T10:47:27.045732Z",
"counterparty": "none",
"counterparty_checked_at": null,
"sanctions": "checked",
"sanctions_checked_at": "2023-12-18T10:47:27.045732Z"
}
}

How to register a transfer attempt

To register a transfer attempt using /transfers/register-attempt/ endpoint you must define
the following fields:
-​

client_id (optional) - an external ID of the client the transfer will be associated with.

-​

attempt_id (optional) - a unique external ID of the attempt used while registering the
transfer.

-​

direction - the direction of the transfer.

-​

network - the code of the network where the transfer occurred.

-​

input_address (when direction is “incoming”) - the address of a sender of the
transfer.

-​

output_address (when direction is “outgoing”) - the address of a recipient of the
transfer.

-​

token_id (optional)

-​

amount (optional)

Request:

curl -X POST "https://kyt-api.bitok.org/v1/transfers/register-attempt/" \
--header "Content-Type: application/json" \
--header "Accept: application/json" \
--header "API-KEY-ID:{KEY_ID}" \
--header "API-TIMESTAMP:{TIMESTAMP}" \
--header "API-SIGNATURE:{SIGNATURE}" \
--data ‘{
"client_id": "id0001",
"attempt_id": "0a805206bab649a68b3408032a7352e6",
"direction": "outgoing",
"network": "ETH",
"token_id": "0xdac17f958d2ee523a2206206994597c13d831ec7",
"output_address": "0x92a5B444907902dAa39dE28A82EF66AF12e7f170",
"amount": 500
}’

Response:

{
"id": "3c6b874e-f76c-42b4-8a08-e13fc50fa6a5",
"client_id": "id0001",
"attempt_id": "0a805206bab649a68b3408032a7352e6",
"registered_at": "2023-12-18T14:15:02.266520+03:00",
"occurred_at": "2023-12-18T14:15:02.258132+03:00",
"direction": "outgoing",
"risk_level": "undefined",
"network": "ETH",
"token_id": "0xdac17f958d2ee523a2206206994597c13d831ec7",

"token_symbol": "USDT",
"tx_hash": null,
"tx_status": "none",
"input_address": null,
"output_address": "0x92a5b444907902daa39de28a82ef66af12e7f170",
"amount": 500,
"fiat_currency": "USD",
"value_in_fiat": 499.66889865320763,
"check_state": {
"exposure": "none",
"exposure_checked_at": null,
"counterparty": "checking",
"counterparty_checked_at": null,
"sanctions": "none",
"sanctions_checked_at": null
}
}

How to bind a transaction to a transfer attempt
Each transfer attempt could be upgraded to a full transfer binding a transaction by a hash.
To bind a transaction to a transfer attempt using /transfers/{id}/bind-transaction/ endpoint
you must define the following fields:
-​

tx_hash - the hash of the transaction the transfer must belong to.

-​

token_id (required if not defined before) - ID of the token.

-​

output_address (required if not defined before) - the address of a recipient of the
transfer. Required for deposits attempts only.

Request:

curl -X POST
"https://kyt-api.bitok.org/v1/transfers/3c6b874e-f76c-42b4-8a08-e13fc50fa6a5/bind-transaction/" \
--header "Content-Type: application/json" \
--header "Accept: application/json" \
--header "API-KEY-ID:{KEY_ID}" \
--header "API-TIMESTAMP:{TIMESTAMP}" \
--header "API-SIGNATURE:{SIGNATURE}" \
--data ‘{
"tx_hash": "0xc9ebe3254e683705c2553e268b915bf310995bf7540285146901b17fc3b437e6"
}’

Response:

{
"id": "3c6b874e-f76c-42b4-8a08-e13fc50fa6a5",
"client_id": "id0001",
"attempt_id": "0a805206bab649a68b3408032a7352e6",
"registered_at": "2023-12-18T14:15:02.266520+03:00",
"occurred_at": "2023-12-18T14:15:02.258132+03:00",
"direction": "outgoing",
"risk_level": "medium",
"network": "ETH",
"token_id": "0xdac17f958d2ee523a2206206994597c13d831ec7",
"token_symbol": "USDT",
"tx_hash": "0xc9ebe3254e683705c2553e268b915bf310995bf7540285146901b17fc3b437e6",
"tx_status": "binding",
"input_address": null,
"output_address": "0x92a5b444907902daa39de28a82ef66af12e7f170",
"amount": 500,
"fiat_currency": "USD",
"value_in_fiat": 499.67,
"check_state": {
"exposure": "queued",
"exposure_checked_at": null,
"counterparty": "checked",
"counterparty_checked_at": "2023-12-18T11:15:04.733475Z",
"sanctions": "checked",
"sanctions_checked_at": "2023-12-18T11:15:04.733475Z"
}
}

When the transaction is bound the state of the transfer state will be enriched with all
necessary properties.
Request:

curl -X GET "https://kyt-api.bitok.org/v1/transfers/3c6b874e-f76c-42b4-8a08-e13fc50fa6a5/" \
--header "Accept: application/json" \
--header "API-KEY-ID:{KEY_ID}" \
--header "API-TIMESTAMP:{TIMESTAMP}" \
--header "API-SIGNATURE:{SIGNATURE}"

Response:

{
"id": "3c6b874e-f76c-42b4-8a08-e13fc50fa6a5",
"client_id": "id0001",
"attempt_id": "0a805206bab649a68b3408032a7352e6",
"registered_at": "2023-12-18T14:15:02.266520+03:00",
"occurred_at": "2023-12-18T13:52:35+03:00",

"direction": "outgoing",
"risk_level": "medium",
"network": "ETH",
"token_id": "0xdac17f958d2ee523a2206206994597c13d831ec7",
"token_symbol": "USDT",
"tx_hash": "0xc9ebe3254e683705c2553e268b915bf310995bf7540285146901b17fc3b437e6",
"tx_status": "bound",
"input_address": "0x3a2c752d3a78a2234b0caf8d6bcc2ec4c9dedfa8",
"output_address": "0x92a5b444907902daa39de28a82ef66af12e7f170",
"amount": 500,
"fiat_currency": "USD",
"value_in_fiat": 499.67,
"check_state": {
​
"exposure": "checked",
​
"exposure_checked_at": "2023-12-18T11:37:54.204528Z",
​
"counterparty": "checked",
​
"counterparty_checked_at": "2023-12-18T11:37:54.204528Z",
​
"sanctions": "checked",
​
"sanctions_checked_at": "2023-12-18T11:37:54.204528Z"
}
}

Transfer exposure and counterparty
Transfer exposure
One of the most important properties of a transfer is its exposure. The exposure defined the
origin of funds for incoming transfers and the destination of funds for outgoing transfers.
The exposure is a property of a full transfer only,
Usually the exposure is automatically checked when a transaction is bound.
The exposure also may be rechecked using the API.

Transfer counterparty
Another important property of a transfer is its counterparty. The counterparty is represented
by an address exposure and defines a sender of incoming transfers and a recipient for
outgoing transfers.
Firstly the counterparty is a property of a transfer attempt but it is also used for full transfers.

Risks and alerts
R
