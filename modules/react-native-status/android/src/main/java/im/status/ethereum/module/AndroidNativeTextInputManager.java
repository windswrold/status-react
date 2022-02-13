package im.status.ethereum.module;

import androidx.annotation.Nullable;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.uimanager.annotations.ReactProp;
import com.facebook.react.views.textinput.ReactTextInputManager;

public class AndroidNativeTextInputManager extends ReactTextInputManager {

  public static final String REACT_CLASS = "AndroidNativeTextInput";
  ReactApplicationContext mCallerContext;

  public AndroidNativeTextInputManager(ReactApplicationContext reactContext) {
    mCallerContext = reactContext;
  }

  @Override
  public String getName() {
    return REACT_CLASS;
  }
}