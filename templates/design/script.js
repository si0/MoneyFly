// 詳細ボタンを押した時の動作
$(function() {
  $(".open_tab").click(function(){
    $($(this).prev(".more_area")).animate({height: "toggle", opacity: "toggle"}, 150);
  });
});
