# Android SDK Integration Guide

This guide shows the recommended minimal flow for integrating the Achievement-to-Asset Bridge into Android games.

1. Google Sign-In & Play Games
   - Use the Play Games SDK to present achievements as usual.
   - When an achievement is unlocked, provide a "Claim Reward" button.

2. Wallet Linking (EIP-4361 / EIP-191)
   - Flow:
     1. Game calls platform `/nonce` endpoint to get a short-lived nonce.
     2. Player signs the nonce using their wallet (WalletConnect or in-app wallet).
     3. Send `{ walletAddress, nonce, signature }` to `/link` to link the Google account to wallet.

3. Claim flow
   - When player taps "Claim":
     1. Obtain a Google access token (server auth code or access token that can call games.v1).
     2. POST to platform `/claim` with body:
        {
          "achievementId": "<id>",
          "accessToken": "<google_access_token>",
          "walletAddress": "0x...",
          "nonce": "...",
          "signature": "0x..."
        }
     3. The platform returns 202 queued with a `claimId`. Poll for status or receive webhook.

4. Minimal Kotlin example (pseudo):

```kotlin
// after getting google access token and wallet signature
val body = JSONObject().apply {
  put("achievementId", achievementId)
  put("accessToken", googleAccessToken)
  put("walletAddress", wallet)
  put("nonce", nonce)
  put("signature", signature)
}

val request = Request.Builder()
  .url("https://api.yourplatform.com/claim")
  .post(RequestBody.create(MediaType.get("application/json"), body.toString()))
  .build()

client.newCall(request).enqueue(object: Callback {
  override fun onResponse(call: Call, response: Response) {
    // handle queued response: show pending UI and poll status endpoint
  }
  override fun onFailure(call: Call, e: IOException) { /* show error */ }
})
```

5. UX & compliance
   - Show clear text: "This achievement will mint a [tradable/NFT | non-transferable/badge] on [Polygon/ImmutableX]".
   - Provide chain explorer link after minted and a support flow for lost wallets.
