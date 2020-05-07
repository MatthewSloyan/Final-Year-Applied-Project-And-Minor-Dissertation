﻿using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

//This Class writes JSON data to the MongoDB
public class DatabaseManager : MonoBehaviour
{
    private string json;

    //Starts CoRoutine to upload the data
    public void writeToDatabase(string json)
    {
        this.json = json;
        StartCoroutine(Upload());
    }

    //Makes a connections and uploads the session's data
    IEnumerator Upload()
    {
        // Fixed issue with sending JSON through web request. It seems it can't be sent using a POST, so PUT is required.
        // Code adapted from: https://forum.unity.com/threads/posting-json-through-unitywebrequest.476254/
        //UnityWebRequest www = UnityWebRequest.Put("localhost:5000/api/results", json);
        UnityWebRequest www = UnityWebRequest.Put("http://aaronchannon1.pythonanywhere.com/api/results", json);

        www.SetRequestHeader("Content-Type", "application/json");
        yield return www.SendWebRequest();

        // Log error message.
        if (www.isNetworkError || www.isHttpError)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log(www.downloadHandler.text);
        }
    }
}

